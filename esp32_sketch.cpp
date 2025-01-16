/*
  Minimal ESP32 Cam Upload Demo
  Make sure you have the right board selected in Tools > Board:
  For example, "AI Thinker ESP32-CAM" or whichever matches your hardware.
*/
#include "WiFi.h"
#include "WiFiClientSecure.h"
#include "HTTPClient.h"
#include "esp_camera.h"

// Camera pin definitions (for AI Thinker module)
#define PWDN_GPIO_NUM    32
#define RESET_GPIO_NUM   -1
#define XCLK_GPIO_NUM    0
#define SIOD_GPIO_NUM    26
#define SIOC_GPIO_NUM    27
#define Y9_GPIO_NUM      35
#define Y8_GPIO_NUM      34
#define Y7_GPIO_NUM      39
#define Y6_GPIO_NUM      36
#define Y5_GPIO_NUM      21
#define Y4_GPIO_NUM      19
#define Y3_GPIO_NUM      18
#define Y2_GPIO_NUM      5
#define VSYNC_GPIO_NUM   25
#define HREF_GPIO_NUM    23
#define PCLK_GPIO_NUM    22

const char* ssid = "<WIFI_SSID>";
const char* password = "<WIFI_PASSWORD>";
String serverUrl = "http://<YOUR_COMPUTER_IP>:5000/upload";

void setup() {
  Serial.begin(115200);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected!");

  // Configure camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Init with high specs to get decent picture
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  // Initialize camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.println("Camera init failed!");
    return;
  }

  // Capture a frame
  camera_fb_t * fb = esp_camera_fb_get();
  if(!fb) {
    Serial.println("Camera capture failed!");
    return;
  }

  // Prepare HTTP POST
  WiFiClient client;
  HTTPClient http;

  http.begin(client, serverUrl);
  http.addHeader("Content-Type", "multipart/form-data");

  // Build multipart form data
  // We'll embed the JPEG data into the POST
  String boundary = "----ESP32CamBoundary";
  String bodyStart = "--" + boundary + "\r\n" +
                     "Content-Disposition: form-data; name=\"file\"; filename=\"esp32.jpg\"\r\n" +
                     "Content-Type: image/jpeg\r\n\r\n";
  String bodyEnd = "\r\n--" + boundary + "--\r\n";

  // Send the POST request
  int contentLength = bodyStart.length() + fb->len + bodyEnd.length();
  http.addHeader("Content-Length", String(contentLength));

  // Actually write the POST body
  http.writeToStream(&client);
  client.print(bodyStart);
  client.write(fb->buf, fb->len);
  client.print(bodyEnd);

  int httpResponseCode = http.POST("");
  if(httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Server response:");
      Serial.println(response);
  } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
  }

  esp_camera_fb_return(fb);
  http.end();
}

void loop() {
  // Do nothing. You can extend this to capture more frames, or wait for triggers, etc.
}
