package models

import (
	"database/sql/driver"
	"encoding/json"
	"gorm.io/gorm"
	"time"
)

type myinterface []interface{}
type LogModel struct {
	Image       myinterface `json:"image"`
	Device      string      `json:"device"`
	Owner       string      `json:"owner"`
	Fullname    string      `json:"fullname"`
	Description string      `json:"description"`
	EnterTime   time.Time   `json:"enter_time"`
}

type Owner struct {
	Owner string `json:"owner"`
}
type OwnerWithDevice struct {
	Owner  string `json:"owner"`
	Device string `json:"device"`
}
type Device struct {
	gorm.Model
	Name  string `json:"name"`
	Owner string `json:"owner"`
}

func (a *myinterface) Scan(value interface{}) error {
	return json.Unmarshal(value.([]byte), a)
}

func (a myinterface) Value() (driver.Value, error) {
	return json.Marshal(a)
}

func MigrateFaces(db *gorm.DB) error {
	err := db.AutoMigrate(&LogModel{})

	return err
}
