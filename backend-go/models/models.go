package models

import (
	"time"
)

type DeviceReading struct {
	ID          uint      `gorm:"primarykey" json:"-"`
	DeviceID    string    `gorm:"index" json:"device_id"`
	RMSCurrent  float64   `json:"rms_current"`
	Power       float64   `json:"power"`
	DailyEnergy float64   `gorm:"column:dailyEnergy" json:"dailyEnergy"` // Add explicit column name
	Timestamp   int64     `gorm:"index" json:"timestamp"`
	ReceivedAt  time.Time `json:"received_at"`
}

func (DeviceReading) TableName() string {
	return "device_readings"
}

type Budget struct {
	ID                 uint    `gorm:"primarykey" json:"-"`
	MonitoringDeviceID string  `gorm:"index" json:"monitoring_device_id"`
	FeedbackDeviceID   string  `json:"feedback_device_id"`
	Budget             float64 `json:"budget"`
}

// specify the table name
func (Budget) TableName() string {
	return "budget"
}

type RealtimeData struct {
	RMSCurrent  float64 `json:"rms_current"`
	Power       float64 `json:"power"`
	DailyEnergy float64 `json:"dailyEnergy"`
	Timestamp   int64   `json:"timestamp"`
}
