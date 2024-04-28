package models

import (
	"database/sql/driver"
	"encoding/json"
	"faces/user_models"
	"gorm.io/gorm"
)

type myinterface []interface{}
type Faces struct {
	Id          uint        `gorm:"primary key; autoIncrement" json:"id"`
	Embedding   myinterface `json:"embedding"`
	Fullname    string      `json:"fullname" gorm:"not null; unique_index"`
	Description string      `json:"description" gorm:"not null; unique_index"`
	Owner       string      `json:"owner"`
}
type ResultFace struct {
	Embedding   myinterface `json:"embedding"`
	Fullname    string      `json:"fullname" gorm:"not null"`
	Description string      `json:"description" gorm:"not null"`
	Image       myinterface `json:"image"`
	Owner       string      `json:"owner"`
}
type Face struct {
	Image       myinterface `json:"image"`
	Fullname    string      `json:"fullname"`
	Description string      `json:"description"`
	Owner       string      `json:"owner"`
}
type FaceToParse struct {
	Image          myinterface `json:"image"`
	Fullname       string      `json:"fullname"`
	Description    string      `json:"description"`
	OldFullname    string      `json:"old_fullname"`
	OldDescription string      `json:"old_description"`
	Owner          string      `json:"owner"`
}
type RequestFace struct {
	Image string `json:"image"`
}

func (a *myinterface) Scan(value interface{}) error {
	return json.Unmarshal(value.([]byte), a)
}

func (a myinterface) Value() (driver.Value, error) {
	return json.Marshal(a)
}

func MigrateFaces(db *gorm.DB) error {
	err := db.AutoMigrate(&ResultFace{})
	err = db.AutoMigrate(&user_models.Owner{})
	err = db.AutoMigrate(&user_models.Device{})

	return err
}
