package main

import (
	"auth/AuthService/models"
	"auth/AuthService/storage"
	"github.com/gofiber/fiber/v2"
	"github.com/joho/godotenv"
	"gorm.io/gorm"
	"log"
	"net/http"
	"os"
	"time"
)

type Repository struct {
	*gorm.DB
}

func (r *Repository) Register(c *fiber.Ctx) error {
	owner := new(models.User)
	err := c.BodyParser(&owner)
	owner.LastLoginTime = time.Now()

	if err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(fiber.Map{"status": "error", "message": "Review your input", "data": err})
	}
	err = r.DB.Table("users").Create(&owner).Error

	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"status": "error", "message": "Review your input", "data": err})
	}
	Owner := new(models.Owner)
	Owner.Username = owner.Login
	Owner.Password = owner.Password
	err = r.DB.Table("owners").Create(&Owner).Error
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(&fiber.Map{"message": "Cannot create owner"})
	}

	return c.JSON(fiber.Map{"status": "success", "message": "User created", "data": owner})

}

func (r *Repository) Login(c *fiber.Ctx) error {
	owner := new(models.User)
	err := c.BodyParser(&owner)
	if err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(fiber.Map{"status": "error", "message": "Review your input", "data": err})
	}
	err = r.DB.Table("users").Where("login = ? AND password = ?", owner.Login, owner.Password).First(&models.User{}).Error

	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"status": "error", "message": "Couldn't find user", "data": err})
	}
	owner.LastLoginTime = time.Now()
	err = r.DB.Table("users").Where("login = ?", owner.Login).Updates(&owner).Error
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"status": "error", "message": "Couldn't update user", "data": err})
	}
	return c.JSON(fiber.Map{"status": "success", "message": "User found", "data": owner})
}

func (r *Repository) CheckAutoLogin(c *fiber.Ctx) error {
	user := new(models.User)
	err := c.BodyParser(&user)
	if err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(fiber.Map{"status": "error", "message": "Review your input", "data": err})
	}
	err = r.DB.Table("users").Where("IP = ? AND LastLoginTime > ? AND Login = ? AND Password = ?", user.IP, time.Now().Add(time.Minute*-60), user.Login, user.Password).First(&models.User{}).Error
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"status": "error", "message": "Couldn't find user", "data": err})
	}
	return c.JSON(fiber.Map{"status": "success", "message": "User found", "data": user})
}

func (r *Repository) LoginApp(c *fiber.Ctx) error {
	owner := new(models.User)
	err := c.BodyParser(&owner)
	if err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(fiber.Map{"status": "error", "message": "Review your input", "data": err})
	}
	err = r.DB.Table("users").Where("login = ? AND password = ?", owner.Login, owner.Password).First(&models.User{}).Error

	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"status": "error", "message": "Couldn't find user", "data": err})
	}
	owner.LastLoginTime = time.Now()
	err = r.DB.Table("users").Where("login = ?", owner.Login).Updates(&owner).Error
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"status": "error", "message": "Couldn't update user", "data": err})
	}
	return c.JSON(fiber.Map{"status": "success", "message": "User found", "data": owner})
}

func (r *Repository) SetupRoutes(app *fiber.App) {
	api := app.Group("/api")
	api.Post("/register", r.Register)
	api.Post("/login", r.Login)

}
func main() {
	err := godotenv.Load(".env")

	config := storage.Config{
		Host:     os.Getenv("DB_HOST"),
		Port:     os.Getenv("DB_PORT"),
		Username: os.Getenv("DB_USERNAME"),
		Password: os.Getenv("DB_PASSWORD"),
		DBName:   os.Getenv("DB_NAME"),
		SSLmode:  os.Getenv("DB_SSLMODE"),
	}
	db, err := storage.NewConnection(config)

	if err != nil {
		log.Fatal("could not load the database")
	}
	err = models.MigrateFaces(db)

	if err != nil {
		log.Fatal("could not migrate the database")
	}
	r := Repository{
		DB: db,
	}

	app := fiber.New(fiber.Config{
		BodyLimit: 4 * 1024 * 1024 * 1024,
	})

	r.SetupRoutes(app)

	app.Listen(":8010")
}
