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

func Init(database *gorm.DB) {
	db = database

	err := godotenv.Load("keys.env")
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	opts := mqtt.NewClientOptions()
	opts.AddBroker(fmt.Sprintf("tcp://%s:%s",
		os.Getenv("BROKER_ADDRESS"),
		os.Getenv("BROKER_PORT")))
	opts.SetUsername(os.Getenv("MOSQUITTO_USER"))
	opts.SetPassword(os.Getenv("MOSQUITTO_PASS"))
	opts.SetClientID("deepwatt_subscriber_go")

	client := mqtt.NewClient(opts)
	if token := client.Connect(); token.Wait() && token.Error() != nil {
		panic(token.Error())
	}

	if token := client.Subscribe("deepwatt/#", 0, messageHandler); token.Wait() && token.Error() != nil {
		panic(token.Error())
	}
}

func messageHandler(client mqtt.Client, msg mqtt.Message) {
	deviceID := msg.Topic()[9:] // Extract device ID from topic
	var data models.RealtimeData

	if err := json.Unmarshal(msg.Payload(), &data); err != nil {
		log.Printf("Error unmarshaling message: %v", err)
		return
	}

	// Store in database
	reading := models.DeviceReading{
		DeviceID:    deviceID,
		RMSCurrent:  data.RMSCurrent,
		Power:       data.Power,
		DailyEnergy: data.DailyEnergy,
		Timestamp:   data.Timestamp,
		ReceivedAt:  time.Now(),
	}

	if result := db.Create(&reading); result.Error != nil {
		log.Printf("Error storing reading: %v", result.Error)
		return
	}

	// Update realtime data
	dataMutex.Lock()
	deviceData[deviceID] = data
	dataMutex.Unlock()
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
