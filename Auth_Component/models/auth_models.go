package models

import (
	"gorm.io/gorm"
	"time"
)

type myinterface []interface{}
type User struct {
	Login         string    `json:"login" gorm:"unique"`
	Password      string    `json:"password"`
	IP            string    `json:"ip"`
	LastLoginTime time.Time `json:"last_login_time"`
}
type IPCheck struct {
	IP string `json:"IP"`
}

type Owner struct {
	gorm.Model
	Username string `json:"username"`
	Password string `json:"password"`
}

func MigrateFaces(db *gorm.DB) error {
	err := db.AutoMigrate(&User{})

	return err
}
