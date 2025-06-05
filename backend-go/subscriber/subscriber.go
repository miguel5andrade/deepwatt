package subscriber

import (
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"time"

	"os"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/joho/godotenv"
	"gorm.io/gorm"

	"deepwatt/backend-go/models"
)

var (
	deviceData = make(map[string]models.RealtimeData)
	dataMutex  sync.RWMutex
	db         *gorm.DB
)
var client mqtt.Client

func Init(database *gorm.DB) {
	db = database
	log.Printf("Subscriber initialized with shared database connection")

	err := godotenv.Load("../keys.env")
	if err != nil {
		log.Printf("Error loading .env file: %v", err)
		// Try current directory as fallback
		err = godotenv.Load("keys.env")
		log.Printf("Loaded keys.env")
		if err != nil {
			log.Fatal("Could not load .env file in either location")
		}
	}

	opts := mqtt.NewClientOptions()
	opts.AddBroker(fmt.Sprintf("tcp://%s:%s",
		os.Getenv("BROKER_ADDRESS"),
		os.Getenv("BROKER_PORT")))
	opts.SetUsername(os.Getenv("MOSQUITTO_USER"))
	opts.SetPassword(os.Getenv("MOSQUITTO_PASS"))
	opts.SetClientID("deepwatt_subscriber_go1")
	opts.SetAutoReconnect(true)
	opts.SetConnectRetry(true)
	opts.OnConnect = connectHandler

	client = mqtt.NewClient(opts)
	if token := client.Connect(); token.Wait() && token.Error() != nil {
		panic(token.Error())
	}

}

func Sub() {
	topic := "deepwatt/#"

	if token := client.Subscribe("deepwatt/#", 0, messageHandler); token.Wait() && token.Error() != nil {
		panic(token.Error())
	}
	log.Printf("Subscribed to the topic %s\n", topic)
}

var connectHandler mqtt.OnConnectHandler = func(client mqtt.Client) {
	log.Println("Connected to the Broker")
	Sub() //subscribe to the topic
}

func messageHandler(client mqtt.Client, msg mqtt.Message) {
	deviceID := msg.Topic()[9:] // Extract device ID from topic
	var data models.RealtimeData
	log.Printf("Received message on topic %s -> Received Payload: %s\n", msg.Topic(), msg.Payload())
	if err := json.Unmarshal(msg.Payload(), &data); err != nil {
		log.Printf("Error unmarshaling message: %v", err)
		return
	}

	// Store in database using shared connection
	reading := models.DeviceReading{
		DeviceID:    deviceID,
		RMSCurrent:  data.RmsCurrent,
		Power:       data.Power,
		DailyEnergy: data.DailyEnergy,
		Timestamp:   data.Timestamp,
		ReceivedAt:  time.Now(),
	}

	if result := db.Create(&reading); result.Error != nil {
		log.Printf("Error storing reading in shared database: %v", result.Error)
		return
	}

	// Update realtime data
	dataMutex.Lock()
	deviceData[deviceID] = data
	dataMutex.Unlock()

	log.Printf("Stored reading for device %s: Power=%.2fW, Energy=%.2fkWh, Current=%.2fA",
		deviceID, data.Power, data.DailyEnergy, data.RmsCurrent)
}

func GetRealtimeData(deviceID string) (models.RealtimeData, bool) {
	dataMutex.RLock()
	defer dataMutex.RUnlock()

	data, exists := deviceData[deviceID]
	if !exists {
		return models.RealtimeData{}, false
	}

	// Check if data is recent (within last 10 seconds)
	if time.Now().Unix()-data.Timestamp > 10 {
		return models.RealtimeData{}, false
	}

	return data, true
}
