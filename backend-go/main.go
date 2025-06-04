package main

import (
	"log"
	"net/http"
	"strconv"
	"time"
	"fmt"
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"

	"deepwatt/backend-go/models"
	"deepwatt/backend-go/subscriber"
)

var db *gorm.DB

func main() {
	// Initialize database
	var err error
	dbPath := "../backend/instance/deepwatt.db"
	db, err = gorm.Open(sqlite.Open(dbPath), &gorm.Config{})
	if err != nil {
		panic("failed to connect database")
	}

	// Migrate the schema
	db.AutoMigrate(&models.DeviceReading{}, &models.Budget{})

	// Initialize MQTT subscriber
	subscriber.Init(db)

	// Initialize Gin router
	gin.SetMode(gin.ReleaseMode)
	r := gin.Default()

	// Configure CORS
	config := cors.DefaultConfig()
	config.AllowAllOrigins = true
	config.AllowCredentials = true
	config.AllowHeaders = []string{"Origin", "Content-Type", "Authorization"}
	r.Use(cors.New(config))

	// Routes
	r.GET("/data/:device_id", getData)
	r.GET("/realtime/:device_id", getRealtimeData)
	r.GET("/budget/:monitoring_device_id", getBudget)
	r.POST("/update-budget/:monitoring_device_id", updateBudget)
	r.GET("/anomalies/:device_id", getAnomalies)

	log.Printf("Starting server on 0.0.0.0:5501")
	if err := r.Run("0.0.0.0:5501"); err != nil {
		log.Fatal(err)
	}
}

func getData(c *gin.Context) {
	deviceID := c.Param("device_id")
	startTime, _ := strconv.ParseInt(c.Query("startTime"), 10, 64)
	endTime, _ := strconv.ParseInt(c.Query("endTime"), 10, 64)
	log.Printf("startTime: %d, endTime: %d\n", startTime, endTime)
	if startTime == 0 || endTime == 0 {
		endTime = time.Now().Unix()
		startTime = endTime - 86400
	}

	log.Printf("Querying data for device %s between %d and %d", deviceID, startTime, endTime)

	var readings []models.DeviceReading
	result := db.Debug().
		Select("id, device_id, rms_current, power, \"dailyEnergy\", timestamp, received_at"). // Explicit column selection
		Where("device_id = ? AND timestamp >= ? AND timestamp <= ?", deviceID, startTime, endTime).
		Find(&readings)

	if result.Error != nil {
		log.Printf("Database error: %v", result.Error)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}

	// Debug print first reading
	if len(readings) > 0 {
		log.Printf("First reading: %+v", readings[0])
	}

	log.Printf("Found %d readings", len(readings))

	// Convert timestamps to ensure they're in the correct format
	for i := range readings {
		if readings[i].Timestamp == 0 {
			readings[i].Timestamp = readings[i].ReceivedAt.Unix()
		}
	}

	c.JSON(http.StatusOK, readings)
}

func getRealtimeData(c *gin.Context) {
	deviceID := c.Param("device_id")

	data, exists := subscriber.GetRealtimeData(deviceID)
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "No data available"})
		return
	}

	c.JSON(http.StatusOK, data)
}

func getBudget(c *gin.Context) {
	monitoringDeviceID := c.Param("monitoring_device_id")

	var budget models.Budget
	if result := db.Where("monitoring_device_id = ?", monitoringDeviceID).First(&budget); result.Error != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "No budget available"})
		return
	}

	c.JSON(http.StatusOK, budget)
}

func updateBudget(c *gin.Context) {
	monitoringDeviceID := c.Param("monitoring_device_id")

	var input struct {
		Budget           float64 `json:"budget"`
		FeedbackDeviceID string  `json:"feedback_device_id"`
	}

	if err := c.BindJSON(&input); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid input"})
		return
	}

	var budget models.Budget
	result := db.Where("monitoring_device_id = ?", monitoringDeviceID).First(&budget)

	if result.Error != nil {
		// Create new budget
		budget = models.Budget{
			MonitoringDeviceID: monitoringDeviceID,
			Budget:             input.Budget,
			FeedbackDeviceID:   input.FeedbackDeviceID,
		}
		db.Create(&budget)
	} else {
		// Update existing budget
		budget.Budget = input.Budget
		budget.FeedbackDeviceID = input.FeedbackDeviceID
		db.Save(&budget)
	}

	c.JSON(http.StatusOK, gin.H{"message": "Budget updated successfully"})
}

func getAnomalies(c *gin.Context) {
	deviceID := c.Param("device_id")
	startTime, _ := strconv.ParseInt(c.Query("startTime"), 10, 64)
	endTime, _ := strconv.ParseInt(c.Query("endTime"), 10, 64)
	fmt.Printf("startTime: %d, endTime: %d\n", startTime, endTime)
	if startTime == 0 || endTime == 0 {
		endTime = time.Now().Unix()
		startTime = endTime - 86400
		fmt.Println("defaulting to one week period")
	}

	var anomalies []models.Anomalies
	result := db.Debug().
		Select("id, device_reading_id,device_id, rms_current, timestamp").
		Where("device_id = ? AND timestamp >= ? AND timestamp <= ?", deviceID, startTime, endTime).
		Find(&anomalies)

	if result.Error != nil {
		log.Printf("Database error: %v", result.Error)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}

	c.JSON(http.StatusOK, anomalies)
}
