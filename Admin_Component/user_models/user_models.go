package user_models

import (
	"gorm.io/gorm"
)

type LoginRequest struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

type LoginResponse struct {
	Token string `json:"token"`
}

type Owner struct {
	gorm.Model
	Username string `gorm:"unique"`
	Password string
}

type Device struct {
	gorm.Model
	Owner string `json:"owner"`
	Name  string `json:"name"`
}

type DeviceToParse struct {
	gorm.Model
	Owner   string `json:"owner"`
	Name    string `json:"name"`
	OldName string `json:"old_name"`
}

type OwnerOld struct {
	Username    string `json:"username"`
	Password    string `json:"password"`
	OldUsername string `json:"old_username"`
	OldPassword string `json:"old_password"`
}

type OwnerToParse struct {
	Owner string `json:"owner"`
}
