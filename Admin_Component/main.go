package main

import (
	"bytes"
	"encoding/json"
	"faces/models"
	"faces/storage"
	"faces/user_models"
	"fmt"
	"github.com/gofiber/fiber/v2"
	"github.com/joho/godotenv"
	"gorm.io/gorm"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
)

type Embedding struct {
	Embedding []interface{} `json:"embedding"`
	Image     []interface{} `json:"image"`
}
type Repository struct {
	*gorm.DB
}

func GetEmbedding(face models.Face) ([]interface{}, []interface{}) {

	client := &http.Client{}

	reqURL, err := url.Parse("http://localhost:8070/get_embedding")
	if err != nil {
		log.Fatal(err)
	}
	values := map[string]interface{}{"image": face.Image}

	jsonValue, _ := json.Marshal(values)

	req, err := http.NewRequest("GET", reqURL.String(), bytes.NewBuffer(jsonValue))
	if err != nil {
		log.Fatal(err)
	}

	resp, err := client.Do(req)
	if err != nil {
		log.Fatal(err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Fatal(err)
	}

	var response Embedding
	err = json.Unmarshal(body, &response)
	if err != nil {
		log.Fatal(err)
	}

	return response.Embedding, response.Image

}
func GetEmbeddingToParse(face models.FaceToParse) ([]interface{}, []interface{}) {

	client := &http.Client{}

	reqURL, err := url.Parse("http://localhost:8070/get_embedding")
	if err != nil {
		log.Fatal(err)
	}
	values := map[string]interface{}{"image": face.Image}

	jsonValue, _ := json.Marshal(values)

	req, err := http.NewRequest("GET", reqURL.String(), bytes.NewBuffer(jsonValue))
	if err != nil {
		log.Fatal(err)
	}

	resp, err := client.Do(req)
	if err != nil {
		log.Fatal(err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Fatal(err)
	}

	var response Embedding
	err = json.Unmarshal(body, &response)
	if err != nil {
		log.Fatal(err)
	}

	return response.Embedding, response.Image

}
func (r *Repository) AddOwner(c *fiber.Ctx) error {
	Owner := &user_models.Owner{}
	c.Set("Access-Control-Allow-Origin", "*")
	if err := c.BodyParser(&Owner); err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(&fiber.Map{"status": "fail", "message": err.Error()})
	}
	err := r.DB.Table("owners").Where("username = ?", Owner.Username).First(&user_models.Owner{}).Error
	if err == nil {
		return c.Status(http.StatusBadRequest).JSON(&fiber.Map{"message": "Owner already exist"})
	}
	r.DB.Table("owners").Create(&Owner)
	return c.Status(http.StatusOK).JSON(&fiber.Map{"message": "User successfully created", "data": &fiber.Map{"user": Owner}})
}
func (r *Repository) UpdateOwner(c *fiber.Ctx) error {
	c.Set("Access-Control-Allow-Origin", "*")
	NewOwner := &user_models.Owner{}
	Owner := &user_models.OwnerOld{}
	if err := c.BodyParser(&Owner); err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(&fiber.Map{"status": "fail", "message": err.Error()})
	}
	NewOwner.Username = Owner.Username
	NewOwner.Password = Owner.Password
	err := r.DB.Table("owners").Where("username = ?", Owner.OldUsername).First(&user_models.Owner{}).Error
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(&fiber.Map{"status": "fail", "message": "Owner does not exist"})
	}
	r.DB.Table("owners").Where("username = ?", Owner.OldUsername).Updates(&NewOwner)
	return c.Status(http.StatusOK).JSON(&fiber.Map{"message": "Owner successfully updated"})

}

func (r *Repository) DeleteOwner(c *fiber.Ctx) error {
	c.Set("Access-Control-Allow-Origin", "*")
	Owner := &user_models.Owner{}
	if err := c.BodyParser(&Owner); err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(&fiber.Map{"status": "fail", "message": err.Error()})
	}
	err := r.DB.Table("owners").Where("username = ?", Owner.Username).First(&user_models.Owner{}).Error
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(&fiber.Map{"status": "fail", "message": "Owner does not exist"})
	}
	r.DB.Table("owners").Where("username = ?", Owner.Username).Delete(&user_models.Owner{})
	return c.Status(http.StatusOK).JSON(&fiber.Map{"message": "Owner successfully deleted"})
}

func (r *Repository) AddDevice(c *fiber.Ctx) error {
	device := &user_models.Device{}
	c.Set("Access-Control-Allow-Origin", "*")
	if err := c.BodyParser(&device); err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(&fiber.Map{"status": "fail", "message": err.Error()})
	}
	err := r.DB.Table("owners").Where("username = ?", device.Owner).First(&user_models.Owner{}).Error
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(&fiber.Map{"status": "fail", "message": "Owner does not exist"})
	}
	err = r.DB.Table("devices").Where("name = ? and owner = ?", device.Name, device.Owner).First(&user_models.Device{}).Error

	if err == nil {
		return c.Status(http.StatusBadRequest).JSON(&fiber.Map{"status": "fail", "message": "Device already exists"})

	}
	r.DB.Table("devices").Create(&device)
	return c.Status(http.StatusOK).JSON(&fiber.Map{"message": "Device successfully created", "data": &fiber.Map{"device": device}})

}

func (r *Repository) UpdateDevice(c *fiber.Ctx) error {
	c.Set("Access-Control-Allow-Origin", "*")
	device := &user_models.DeviceToParse{}
	new_device := &user_models.Device{}
	if err := c.BodyParser(&device); err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(&fiber.Map{"status": "fail", "message": err.Error()})
	}
	new_device.Name = device.Name
	new_device.Owner = device.Owner
	err := r.DB.Table("devices").Where("name = ? and owner = ?", device.OldName, device.Owner).First(&user_models.Device{}).Error
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(&fiber.Map{"status": "fail", "message": "Device does not exist"})
	}
	fmt.Println(new_device)
	r.DB.Table("devices").Model(&user_models.Device{}).Where("name = ? and owner = ?", device.OldName, device.Owner).Updates(&new_device)

	return c.Status(http.StatusOK).JSON(&fiber.Map{"message": "Device successfully updated"})

}
func (r *Repository) DeleteDevice(c *fiber.Ctx) error {
	c.Set("Access-Control-Allow-Origin", "*")
	device := &user_models.Device{}

	if err := c.BodyParser(&device); err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(&fiber.Map{"status": "fail", "message": err.Error()})
	}
	err := r.DB.Table("devices").Where("name = ? and owner = ?", device.Name, device.Owner).First(&user_models.Device{}).Error
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(&fiber.Map{"status": "fail", "message": "Device does not exist"})
	}
	r.DB.Table("devices").Where("name = ? and owner = ?", device.Name, device.Owner).Delete(&user_models.Device{})

	return c.Status(http.StatusOK).JSON(&fiber.Map{"message": "Device successfully deleted"})
}

func (r *Repository) GetFaces(c *fiber.Ctx) error {
	c.Set("Access-Control-Allow-Origin", "*")
	owner := user_models.OwnerToParse{}
	err := c.BodyParser(&owner)
	if err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(&fiber.Map{"status": "fail", "message": err.Error()})
	}
	face_models := []models.ResultFace{}
	err = r.DB.Table("result_faces").Where("owner = ?", owner.Owner).Find(&face_models).Error

	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(&fiber.Map{"message": "could not get books"})
	}
	return c.Status(http.StatusOK).JSON(&fiber.Map{"message": "books fetched successfully", "data": face_models})

}

func (r *Repository) GetDevices(c *fiber.Ctx) error {
	c.Set("Access-Control-Allow-Origin", "*")
	owner := user_models.OwnerToParse{}
	err := c.BodyParser(&owner)
	if err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(&fiber.Map{"status": "fail", "message": err.Error()})
	}

	devices := []user_models.Device{}
	err = r.DB.Table("devices").Where("owner = ?", owner.Owner).Find(&devices).Error
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(&fiber.Map{"message": "could not get devices"})
	}
	return c.Status(http.StatusOK).JSON(&fiber.Map{"message": "devices fetched successfully", "data": devices})

}

func (r *Repository) UpdateFace(c *fiber.Ctx) error {
	face := models.FaceToParse{}
	err := c.BodyParser(&face)
	c.Set("Access-Control-Allow-Origin", "*")

	if err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(fiber.Map{"message": "request error"})
	}
	if err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(fiber.Map{"message": "combination must be unique"})
	}

	resultFace := models.ResultFace{}
	resultFace.Description = face.Description
	resultFace.Fullname = face.Fullname
	resultFace.Embedding, resultFace.Image = GetEmbeddingToParse(face)
	resultFace.Owner = face.Owner
	if resultFace.Embedding == nil {
		return c.Status(http.StatusOK).JSON(fiber.Map{"message": "No face or more than one face on image", "face": nil})
	}

	tx := r.DB.Table("result_faces").Model(&models.ResultFace{}).Where("fullname = ? AND description = ?", face.OldFullname, face.OldDescription).Updates(&resultFace)
	if tx.Error != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "this face don't exist"})
	}
	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "face updated successfully", "face": resultFace})
}
func (r *Repository) CreateFace(c *fiber.Ctx) error {
	face := models.Face{}
	err := c.BodyParser(&face)
	c.Set("Access-Control-Allow-Origin", "*")
	if err != nil {
		return c.Status(http.StatusUnprocessableEntity).JSON(fiber.Map{"message": "request error"})
	}
	ResultFace := models.ResultFace{}
	ResultFace.Description = face.Description
	ResultFace.Fullname = face.Fullname
	ResultFace.Owner = face.Owner
	ResultFace.Embedding, ResultFace.Image = GetEmbedding(face)
	if ResultFace.Embedding == nil {
		return c.Status(http.StatusOK).JSON(fiber.Map{"message": "No face or more than one face on image", "face": nil})
	}

	tx := r.DB.Table("result_faces").Create(&ResultFace)

	if tx.Error != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "could not create face"})
	}
	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "face created successfully", "face": ResultFace})
}
func (r *Repository) DeleteFace(c *fiber.Ctx) error {
	face := models.ResultFace{}
	c.Set("Access-Control-Allow-Origin", "*")

	err := c.BodyParser(&face)
	if face.Fullname == "" {
		return c.Status(http.StatusInternalServerError).JSON(&fiber.Map{"message": "id cannot be empty"})
	}
	fmt.Println(face)
	err = r.DB.Table("result_faces").Where("fullname = ? AND description = ? AND owner = ?", face.Fullname, face.Description, face.Owner).Delete(&face).Error
	if err != nil {
		return c.Status(http.StatusBadRequest).JSON(fiber.Map{"message": "could not delete a book"})
	}

	return c.Status(http.StatusOK).JSON(fiber.Map{"message": "face deleted successfully", "face": face})
}

func (r *Repository) SetupRoutes(app *fiber.App) {
	api := app.Group("/api")
	api.Post("/create_face/", r.CreateFace)
	api.Delete("/delete_face/", r.DeleteFace)
	api.Put("/update_face/", r.UpdateFace)
	api.Post("/create_owner/", r.AddOwner)
	api.Post("/create_device/", r.AddDevice)
	api.Post("/get_devices/", r.GetDevices)
	api.Post("/get_faces/", r.GetFaces)
	api.Put("/update_device/", r.UpdateDevice)
	api.Delete("/delete_device/", r.DeleteDevice)
	api.Delete("/delete_owner/", r.DeleteOwner)
	api.Put("/update_owner/", r.UpdateOwner)
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

	app.Listen(":8080")
}
