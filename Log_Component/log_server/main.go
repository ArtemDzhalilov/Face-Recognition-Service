package main

import (
	"github.com/gofiber/fiber/v2"
	"github.com/joho/godotenv"
	"gorm.io/gorm"
	"log"
	"log/log_server/models"
	"log/log_server/storage"
	"net/http"
	"os"
	"time"
)

type Repository struct {
	*gorm.DB
}

func (r *Repository) CreateLog(c *fiber.Ctx) error {
	log := models.LogModel{}

	if err := c.BodyParser(&log); err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(fiber.Map{"message": err})

	}
	log.EnterTime = time.Now()
	err := r.DB.Table("log_models").Create(&log).Error
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"message": err})
	}
	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "success"})
}
func (r *Repository) GetLogs(c *fiber.Ctx) error {
	owner := models.Owner{}
	logs := []models.LogModel{}
	if err := c.BodyParser(&owner); err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(fiber.Map{"message": err})
	}
	err := r.DB.Table("log_models").Where("owner = ?", owner.Owner).Find(&logs).Error
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"message": err})
	}
	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "success", "data": logs})
}
func (r *Repository) GetLogsByDevice(c *fiber.Ctx) error {
	owner := models.OwnerWithDevice{}
	logs := []models.LogModel{}
	if err := c.BodyParser(&owner); err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(fiber.Map{"message": err})
	}
	err := r.DB.Table("log_models").Where("owner = ? AND device = ?", owner.Owner, owner.Device).Find(&logs).Error
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"message": err})
	}
	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "success", "data": logs})
}
func (r *Repository) DeleteLog(c *fiber.Ctx) error {
	log := models.LogModel{}

	if err := c.BodyParser(&log); err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(fiber.Map{"message": err})
	}
	err := r.DB.Table("log_models").Where(&log).Delete(&models.LogModel{}).Error
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"message": err})
	}
	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "success"})
}
func (r *Repository) DeleteLogs(c *fiber.Ctx) error {
	owner := models.Owner{}

	if err := c.BodyParser(&owner); err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(fiber.Map{"message": err})
	}
	err := r.DB.Table("log_models").Where("owner = ?", owner.Owner).Delete(&models.LogModel{}).Error
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"message": err})
	}
	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "success"})
}
func (r *Repository) GetAllLogs(c *fiber.Ctx) error {
	logs := []models.LogModel{}
	err := r.DB.Table("log_models").Find(&logs).Error
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(fiber.Map{"message": err})
	}
	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "success", "data": logs})

}

func autoDelete(db *gorm.DB) {
	ticker := time.NewTicker(24 * time.Hour)
	go func() {
		for {
			select {
			case <-ticker.C:
				oneMonthAgo := time.Now().AddDate(0, -1, 0).Unix()
				db.Delete(&models.LogModel{}, "enter_time < ?", oneMonthAgo)
			}
		}
	}()
}
func (r *Repository) SetupRoutes(app *fiber.App) {
	api := app.Group("/api")
	api.Post("/create_log", r.CreateLog)
	api.Post("/get_logs", r.GetLogs)
	api.Delete("/delete_logs", r.DeleteLogs)
	api.Delete("/delete_log", r.DeleteLog)
	api.Get("/get_all_logs", r.GetAllLogs)
	api.Post("/get_logs_by_device", r.GetLogsByDevice)
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

	app.Listen(":8090")
	autoDelete(r.DB)
}
