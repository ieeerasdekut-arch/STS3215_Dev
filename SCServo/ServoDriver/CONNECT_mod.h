// // https://randomnerdtutorials.com/esp32-useful-wi-fi-functions-arduino/
// #include <esp_now.h>
// #include <WiFi.h>
// #include <WebServer.h>
// #include "WEBPAGE.h"

// // Create WebServer object on port 80
// WebServer server(80);

// // ==========================================
// // === NEW PYTHON API FUNCTIONS (ADDED)   ===
// // ==========================================

// void handleMove() {
//   // USAGE: http://IP/move?id=1&pos=2048&spd=1000&acc=50
//   if (server.hasArg("id") && server.hasArg("pos")) {
//     int id = server.arg("id").toInt();
//     int pos = server.arg("pos").toInt();
//     int spd = server.arg("spd").toInt(); // Default 0 if missing
//     int acc = server.arg("acc").toInt(); // Default 0 if missing

//     Serial.print("pos: ");
//     Serial.print(pos);
//     Serial.print("  spd: ");
//     Serial.print(spd);
//     Serial.print("  acc: ");
//     Serial.println(acc);
    

//     // If speed is 0 or missing, use a safe default
//     if (spd <= 0) spd = 1000;
    
//     // Call the library function directly
//     // This bypasses the preset buttons and gives you full control
//     st.WritePosEx(id, pos, spd, acc);
    
//     server.send(200, "text/plain", "OK: Moved ID " + String(id));
//   } else {
//     server.send(400, "text/plain", "Error: Missing id or pos arguments");
//   }
// }

// void handleTorque() {
//   // USAGE: http://IP/torque?id=1&en=1 (1=ON, 0=OFF)
//   if (server.hasArg("id") && server.hasArg("en")) {
//     int id = server.arg("id").toInt();
//     int en = server.arg("en").toInt();
    
//     st.EnableTorque(id, en);
    
//     // Update internal state array so the webpage UI stays in sync
//     if(id < 253) {
//       Torque_List[id] = (en == 1);
//     }
    
//     server.send(200, "text/plain", "OK: Torque set");
//   } else {
//     server.send(400, "text/plain", "Error: Missing id or en arguments");
//   }
// }

// void handleFeedback() {
//   // USAGE: http://IP/feedback?id=1
//   // Returns JSON: {"id":1, "pos":2048, "spd":0, "load":10, "volt":12.1, "temp":45, "curr":0}
//   if (server.hasArg("id")) {
//     int id = server.arg("id").toInt();
    
//     // Force a fresh immediate read from the motor
//     int result = st.FeedBack(id);
    
//     if (result != -1) {
//       int pos = st.ReadPos(-1);
//       int spd = st.ReadSpeed(-1);
//       int load = st.ReadLoad(-1);
//       int volt = st.ReadVoltage(-1);
//       int temp = st.ReadTemper(-1);
//       int curr = st.ReadCurrent(-1);
//       int move = st.ReadMove(-1);

//       // Construct JSON String manually
//       String json = "{";
//       json += "\"id\":" + String(id) + ",";
//       json += "\"pos\":" + String(pos) + ",";
//       json += "\"spd\":" + String(spd) + ",";
//       json += "\"load\":" + String(load) + ",";
//       json += "\"volt\":" + String(float(volt)/10.0) + ","; // Convert to Volts
//       json += "\"curr\":" + String(curr) + ",";
//       json += "\"temp\":" + String(temp) + ",";
//       json += "\"move\":" + String(move);
//       json += "}";
      
//       server.send(200, "application/json", json);
//     } else {
//       server.send(500, "application/json", "{\"error\":\"Timeout/No Response\"}");
//     }
//   } else {
//     server.send(400, "text/plain", "Error: Missing id argument");
//   }
// }

// // ==========================================
// // === ORIGINAL FACTORY FUNCTIONS (KEPT)  ===
// // ==========================================

// // select the ID of active servo.
// void activeID(int cmdInput){
//   activeNumInList += cmdInput;
//   if(activeNumInList >= searchNum){
//     activeNumInList = 0;
//   }
//   else if(activeNumInList < 0){
//     activeNumInList = searchNum;
//   }
// }

// void activeSpeed(int cmdInput){
//   activeServoSpeed += cmdInput;
//   if (activeServoSpeed > ServoMaxSpeed){
//     activeServoSpeed = ServoMaxSpeed;
//   }
//   else if(activeServoSpeed < 0){
//     activeServoSpeed = 0;
//   }
// }

// int rangeCtrl(int rawInput, int minInput, int maxInput){
//   if(rawInput > maxInput){
//     return maxInput;
//   }
//   else if(rawInput < minInput){
//     return minInput;
//   }
//   else{
//     return rawInput;
//   }
// }

// void activeCtrl(int cmdInput){
//   switch(cmdInput){
//     case 1:st.WritePosEx(listID[activeNumInList], ServoDigitalMiddle, activeServoSpeed, ServoInitACC);break;
//     case 2:
//       if(modeRead[listID[activeNumInList]] == 0) {
//         servoStop(listID[activeNumInList]);
//       }
//       else if(modeRead[listID[activeNumInList]] == 3){
//         st.WritePosEx(listID[activeNumInList], 0, 0, 0);
//       }
//       break;
//     case 3:servoTorque(listID[activeNumInList],0);Torque_List[activeNumInList] = false;break;
//     case 4:servoTorque(listID[activeNumInList],1);Torque_List[activeNumInList] = true;break;
//     case 5:
//       if(modeRead[listID[activeNumInList]] == 0){
//         if(SERVO_TYPE_SELECT == 1){
//           st.WritePosEx(listID[activeNumInList], ServoDigitalRange - 1, activeServoSpeed, ServoInitACC);
//         }
//         else if(SERVO_TYPE_SELECT == 2){
//           st.WritePosEx(listID[activeNumInList], ServoDigitalRange - MAX_MIN_OFFSET, activeServoSpeed, ServoInitACC);
//         }
//       }

//       else if(modeRead[listID[activeNumInList]] == 3){
//         if(SERVO_TYPE_SELECT == 1){
//           st.WritePosEx(listID[activeNumInList], 10000, activeServoSpeed, ServoInitACC);
//         }
//         else if(SERVO_TYPE_SELECT == 2){
//           st.WritePosEx(listID[activeNumInList], 0, rangeCtrl(activeServoSpeed,200,999), 0);
//         }
//       }
//       break;
//     case 6:
//       if(modeRead[listID[activeNumInList]] == 0){
//         if(SERVO_TYPE_SELECT == 1){
//           st.WritePosEx(listID[activeNumInList], 0, activeServoSpeed, ServoInitACC);
//         }
//         else if(SERVO_TYPE_SELECT == 2){
//           st.WritePosEx(listID[activeNumInList], MAX_MIN_OFFSET, activeServoSpeed, ServoInitACC);
//         }
//       }

//       else if(modeRead[listID[activeNumInList]] == 3){
//         if(SERVO_TYPE_SELECT == 1){
//           st.WritePosEx(listID[activeNumInList], -10000, activeServoSpeed, ServoInitACC);
//         }
//         else if(SERVO_TYPE_SELECT == 2){
//           st.WritePosEx(listID[activeNumInList], 0, rangeCtrl(activeServoSpeed,200,999)+1024, 0);
//         }
//       }
//       break;
//     case 7:activeSpeed(100);break;
//     case 8:activeSpeed(-100);break;
//     case 9:servotoSet += 1;if(servotoSet > 250){servotoSet = 0;}break;
//     case 10:servotoSet -= 1;if(servotoSet < 0){servotoSet = 0;}break;
//     case 11:setMiddle(listID[activeNumInList]);break;
//     case 12:setMode(listID[activeNumInList], 0);break;
//     case 13:setMode(listID[activeNumInList], 3);break;
//     case 14:SERIAL_FORWARDING = true;break;
//     case 15:SERIAL_FORWARDING = false;break;
//     case 16:setID(listID[activeNumInList], servotoSet);break;

//     case 17:DEV_ROLE = 0;break;
//     case 18:DEV_ROLE = 1;break;
//     case 19:DEV_ROLE = 2;break;

//     case 20:RAINBOW_STATUS = 1;break;
//     case 21:RAINBOW_STATUS = 0;break;
//   }
// }

// void handleRoot() {
//  server.send(200, "text/html", index_html); //Send web page
// }

// void handleID() {
//   if(!searchedStatus && searchFinished){
//     String IDmessage = "ID:";
//     for(int i = 0; i< searchNum; i++){
//       IDmessage += String(listID[i]) + " ";
//     }
//     server.send(200, "text/plane", IDmessage);
//   }
//   else if(searchedStatus){
//     String IDmessage = "Searching...";
//     server.send(200, "text/plane", IDmessage);
//   }
// }

// void handleSTS() {
//   String stsValue = "Active ID:" + String(listID[activeNumInList]);
//   if(voltageRead[listID[activeNumInList]] != -1){
//     stsValue += "  Position:" + String(posRead[listID[activeNumInList]]);
//     if(DEV_ROLE == 0){
//       stsValue += "<p>Device Mode: Normal";
//     }
//     else if(DEV_ROLE == 1){
//       stsValue += "<p>Device Mode: Leader";
//     }
//     else if(DEV_ROLE == 2){
//       stsValue += "<p>Device Mode: Follower";
//     }
//     stsValue += "<p>Voltage:" + String(float(voltageRead[listID[activeNumInList]])/10);
//     stsValue += "  Load:" + String(loadRead[listID[activeNumInList]]);
//     stsValue += "<p>Speed:" + String(speedRead[listID[activeNumInList]]);

//     stsValue += "  Temper:" + String(temperRead[listID[activeNumInList]]);
//     stsValue += "<p>Speed Set:" + String(activeServoSpeed);
//     stsValue += "<p>ID to Set:" + String(servotoSet);
//     stsValue += "<p>Mode:";
//     if(modeRead[listID[activeNumInList]] == 0){
//       stsValue += "Servo Mode";
//     }
//     else if(modeRead[listID[activeNumInList]] == 3){
//       stsValue += "Motor Mode";
//     }

//     if(Torque_List[activeNumInList]){
//       stsValue += "<p>Torque On";
//     }
//     else{
//       stsValue += "<p>Torque Off";
//     }
//   }
//   else{
//     stsValue += " FeedBack err";
//   }
//   server.send(200, "text/plane", stsValue); //Send ADC value only to client ajax request
// }

// // ==========================================
// // === MODIFIED SERVER SETUP              ===
// // ==========================================

// void webCtrlServer(){
//     // Original Handles
//     server.on("/", handleRoot);
//     server.on("/readID", handleID);
//     server.on("/readSTS", handleSTS);

//     // NEW Python API Handles
//     server.on("/move", handleMove);
//     server.on("/torque", handleTorque);
//     server.on("/feedback", handleFeedback);

//     // Original Command Handler for Web Interface Buttons
//     server.on("/cmd", [](){
//       int cmdT = server.arg(0).toInt();
//       int cmdI = server.arg(1).toInt();
//       int cmdA = server.arg(2).toInt();
//       int cmdB = server.arg(3).toInt();

//       switch(cmdT){
//         case 0:activeID(cmdI);break;
//         case 1:activeCtrl(cmdI);break;
//         case 9:searchCmd = true;break;
//       }
//       server.send(200, "text/plain", "OK");
//     });

//   // Start server
//   server.begin();
//   Serial.println("Server Starts.");
// }

// void webServerSetup(){
//   webCtrlServer();
// }

// void getMAC(){
//   WiFi.mode(WIFI_AP_STA);
//   MAC_ADDRESS = WiFi.macAddress();
//   Serial.print("MAC:");
//   Serial.println(WiFi.macAddress());
// }

// void getIP(){
//   IP_ADDRESS = WiFi.localIP();
// }

// void setAP(){
//   WiFi.softAP(AP_SSID, AP_PWD);
//   IPAddress myIP = WiFi.softAPIP();
//   IP_ADDRESS = myIP;
//   Serial.print("AP IP address: ");
//   Serial.println(myIP);
//   WIFI_MODE = 1;
// }

// void setSTA(){
//   WIFI_MODE = 3;
//   WiFi.begin(STA_SSID, STA_PWD);
// }

// void getWifiStatus(){
//   if(WiFi.status() == WL_CONNECTED){
//     WIFI_MODE = 2;
//     getIP();
//     WIFI_RSSI = WiFi.RSSI();
//   }
//   else if(WiFi.status() == WL_CONNECTION_LOST && DEFAULT_WIFI_MODE == 2){
//     WIFI_MODE = 3;
//     // WiFi.disconnect();
//     WiFi.reconnect();
//   }
// }

// void wifiInit(){
//   DEV_ROLE  = DEFAULT_ROLE;
//   WIFI_MODE = DEFAULT_WIFI_MODE;
//   if(WIFI_MODE == 1){setAP();}
//   else if(WIFI_MODE == 2){setSTA();}
// }

// void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
//   Serial.print("\r\nLast Packet Send Status:\t");
//   Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
// }

// void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
//   if(DEV_ROLE == 2){
//     memcpy(&myData, incomingData, sizeof(myData));
//     myData.Spd_send = abs(myData.Spd_send);
//     if(myData.Spd_send < 50){
//       myData.Spd_send = 200;
//     }
//     st.WritePosEx(myData.ID_send, myData.POS_send, abs(myData.Spd_send), 0);

//     Serial.print("Bytes received: ");
//     Serial.println(len);
//     Serial.print("POS: ");
//     Serial.println(myData.POS_send);
//     Serial.print("SPEED: ");
//     Serial.println(abs(myData.Spd_send));
//   }
// }

// void espNowInit(){
//   // Set device as a Wi-Fi Station
//   WiFi.mode(WIFI_STA);

//   // Init ESP-NOW
//   if (esp_now_init() != ESP_OK) {
//     Serial.println("Error initializing ESP-NOW");
//     return;
//   }

//   // Once ESPNow is successfully Init, we will register for Send CB to
//   // get the status of Trasnmitted packet
//   esp_now_register_send_cb(OnDataSent);
//   esp_now_register_recv_cb(OnDataRecv);

//   // Register peer
//   esp_now_peer_info_t peerInfo;
//   memcpy(peerInfo.peer_addr, broadcastAddress, 6);
//   peerInfo.channel = 0;  
//   peerInfo.encrypt = false;
  
//   // Add peer        
//   if (esp_now_add_peer(&peerInfo) != ESP_OK){
//     Serial.println("Failed to add peer");
//     return;
//   }

//   MAC_ADDRESS = WiFi.macAddress();
//   Serial.print("MAC:");
//   Serial.println(WiFi.macAddress());
// }


// https://randomnerdtutorials.com/esp32-useful-wi-fi-functions-arduino/
#include <esp_now.h>
#include <WiFi.h>
#include <WebServer.h>
#include "WEBPAGE.h"
#include <ESP32Servo.h> 

int base_m_position = 0;

// Create WebServer object on port 80
WebServer server(80);

Servo gripperServo;             // <--- ADD THIS
const int GRIPPER_PIN = 13; 

// ==========================================
// === NEW PYTHON API FUNCTIONS           ===
// ==========================================

void handleMove() {
  // USAGE: http://IP/move?id=1&pos=2048&spd=1000&acc=50
  if (server.hasArg("id") && server.hasArg("pos")) {
    int id = server.arg("id").toInt();
    int pos = server.arg("pos").toInt();
    int spd = server.arg("spd").toInt(); // Default 0 if missing
    int acc = server.arg("acc").toInt(); // Default 0 if missing

    if(id == 0){
      base_m_position = pos;
    }

    // If speed is 0, use a safe default
    if (spd <= 0) spd = 1000;
    
    // Call the library function directly
    st.WritePosEx(id, pos, spd, acc);
    Serial.print("Moved id: ");Serial.print(id);Serial.print(" to ") ;Serial.println(pos);
    
    server.send(200, "text/plain", "OK: Moved ID " + String(id) + " to " + String(pos));
  } else {
    server.send(400, "text/plain", "Error: Missing id or pos args");
  }
}

// void handleGripper() {//for esp now
//   // USAGE: http://IP/gripper?pos=90
//   // pos: 0 to 180 (standard SG90 angle)
//   if (server.hasArg("pos")) {
//     int pos = server.arg("pos").toInt();
    
//     // Populate the existing ESP-NOW struct
//     myData.ID_send = 99;   // 99 means "Gripper"
//     myData.POS_send = pos; // The angle for the SG90
//     myData.Spd_send = 0;   // Not used for the SG90
    
//     // Send the message via ESP-NOW
//     esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *) &myData, sizeof(myData));
    
//     if (result == ESP_OK) {
//       server.send(200, "text/plain", "OK: Gripper set to " + String(pos));
//     } else {
//       server.send(500, "text/plain", "Error: ESP-NOW broadcast failed");
//     }
//   } else {
//     server.send(400, "text/plain", "Error: Missing pos arg");
//   }
// }

void handleGripper() {//hardwired servo
  // USAGE: http://IP/gripper?pos=90
  if (server.hasArg("pos")) {
    int pos = server.arg("pos").toInt();
    
    // Constrain for SG90 safety
    if (pos < 0) pos = 0;
    if (pos > 180) pos = 180;
    
    gripperServo.write(pos);
    Serial.print("Gripper moved to: ");
    Serial.println(pos);
    server.send(200, "text/plain", "OK: Gripper set to " + String(pos));
  } else {
    server.send(400, "text/plain", "Error: Missing pos arg");
    Serial.println("Servo not moved");
  }
}

void handleCalibrateZero() {
  // USAGE: http://IP/calibrate?id=1
  if (server.hasArg("id")) {
    int id = server.arg("id").toInt();
    
    // Unlock EEPROM, write calibration offset to current position, and lock back
    st.unLockEprom(id);
    delay(10);
    st.CalibrationOfs(id); // Sets current physical position as logical middle (2047)
    delay(10);
    st.LockEprom(id);
    
    Serial.print("[OK] Calibrated zero position for Servo ID: ");
    Serial.println(id);
    
    server.send(200, "text/plain", "OK: Servo " + String(id) + " zero position saved.");
  } else {
    server.send(400, "text/plain", "Error: Missing id argument");
  }
}

void handleMultiTurn() {
  // USAGE: http://IP/multiturn?id=1&en=1
  // en=1: Enables infinite rotation range (needed for gears)
  // en=0: Restricts range to 0-4095
  
  if (server.hasArg("id") && server.hasArg("en")) {
    int id = server.arg("id").toInt();
    int en = server.arg("en").toInt();
    
    setMultiTurn(id, (en == 1));
    
    server.send(200, "text/plain", "OK: MultiTurn Set to" + String(en));
  } else {
    server.send(400, "text/plain", "Missing args");
  }
}

void handleTorque() {
  // USAGE: http://IP/torque?id=1&en=1 (1=ON, 0=OFF)
  if (server.hasArg("id") && server.hasArg("en")) {
    int id = server.arg("id").toInt();
    int en = server.arg("en").toInt();
    
    st.EnableTorque(id, en);
    
    // Update internal state
    if(id < 253) Torque_List[id] = (en == 1);
    
    server.send(200, "text/plain", "OK: Torque set");
  } else {
    server.send(400, "text/plain", "Error: Missing id or en args");
  }
}

void handleMode() {
  // USAGE: http://IP/mode?id=1&val=0  (0=Servo Mode, 3=Motor Mode)
  if (server.hasArg("id") && server.hasArg("val")) {
    int id = server.arg("id").toInt();
    int modeVal = server.arg("val").toInt();
    
    // Calls the helper function from STSCTRL.h
    // This writes to EPROM to permanently set the mode
    setMode(id, modeVal);
    
    server.send(200, "text/plain", "OK: Mode Set to " + String(modeVal));
  } else {
    server.send(400, "text/plain", "Error: Missing id or val args");
  }
}

void handleFeedback() {
  // USAGE: http://IP/feedback?id=1
  if (server.hasArg("id")) {
    int id = server.arg("id").toInt();
    
    // Force a fresh read
    int result = st.FeedBack(id);
    
    if (result != -1) {
      int pos = st.ReadPos(-1);
      int spd = st.ReadSpeed(-1);
      int load = st.ReadLoad(-1);
      int volt = st.ReadVoltage(-1);
      int temp = st.ReadTemper(-1);
      int curr = st.ReadCurrent(-1);
      int move = st.ReadMove(-1);

      if(id == 0){
        pos = - base_m_position;
      }

      String json = "{";
      json += "\"id\":" + String(id) + ",";
      json += "\"pos\":" + String(pos) + ",";
      json += "\"spd\":" + String(spd) + ",";
      json += "\"load\":" + String(load) + ",";
      json += "\"volt\":" + String(float(volt)/10.0) + ",";
      json += "\"curr\":" + String(curr) + ",";
      json += "\"temp\":" + String(temp) + ",";
      json += "\"move\":" + String(move);
      json += "}";
      
      Serial.print("ID: "); Serial.print(id);
      Serial.print("  Pos: "); Serial.print(pos);
      Serial.print(" Move: "); Serial.println(move);

      server.send(200, "application/json", json);
    } else {
      server.send(500, "application/json", "{\"error\":\"Timeout\"}");
    }
  } else {
    server.send(400, "text/plain", "Error: Missing id arg");
  }
}

// ==========================================
// === ORIGINAL FACTORY FUNCTIONS (KEPT)  ===
// ==========================================

void activeID(int cmdInput){
  activeNumInList += cmdInput;
  if(activeNumInList >= searchNum) activeNumInList = 0;
  else if(activeNumInList < 0) activeNumInList = searchNum;
}

void activeSpeed(int cmdInput){
  activeServoSpeed += cmdInput;
  if (activeServoSpeed > ServoMaxSpeed) activeServoSpeed = ServoMaxSpeed;
  else if(activeServoSpeed < 0) activeServoSpeed = 0;
}

int rangeCtrl(int rawInput, int minInput, int maxInput){
  if(rawInput > maxInput) return maxInput;
  else if(rawInput < minInput) return minInput;
  else return rawInput;
}

void activeCtrl(int cmdInput){
  switch(cmdInput){
    case 1:st.WritePosEx(listID[activeNumInList], ServoDigitalMiddle, activeServoSpeed, ServoInitACC);break;
    case 2:
      if(modeRead[listID[activeNumInList]] == 0) servoStop(listID[activeNumInList]);
      else if(modeRead[listID[activeNumInList]] == 3) st.WritePosEx(listID[activeNumInList], 0, 0, 0);
      break;
    case 3:servoTorque(listID[activeNumInList],0);Torque_List[activeNumInList] = false;break;
    case 4:servoTorque(listID[activeNumInList],1);Torque_List[activeNumInList] = true;break;
    case 5:
      if(modeRead[listID[activeNumInList]] == 0){
        if(SERVO_TYPE_SELECT == 1) st.WritePosEx(listID[activeNumInList], ServoDigitalRange - 1, activeServoSpeed, ServoInitACC);
        else if(SERVO_TYPE_SELECT == 2) st.WritePosEx(listID[activeNumInList], ServoDigitalRange - MAX_MIN_OFFSET, activeServoSpeed, ServoInitACC);
      }
      else if(modeRead[listID[activeNumInList]] == 3){
        if(SERVO_TYPE_SELECT == 1) st.WritePosEx(listID[activeNumInList], 10000, activeServoSpeed, ServoInitACC);
        else if(SERVO_TYPE_SELECT == 2) st.WritePosEx(listID[activeNumInList], 0, rangeCtrl(activeServoSpeed,200,999), 0);
      }
      break;
    case 6:
      if(modeRead[listID[activeNumInList]] == 0){
        if(SERVO_TYPE_SELECT == 1) st.WritePosEx(listID[activeNumInList], 0, activeServoSpeed, ServoInitACC);
        else if(SERVO_TYPE_SELECT == 2) st.WritePosEx(listID[activeNumInList], MAX_MIN_OFFSET, activeServoSpeed, ServoInitACC);
      }
      else if(modeRead[listID[activeNumInList]] == 3){
        if(SERVO_TYPE_SELECT == 1) st.WritePosEx(listID[activeNumInList], -10000, activeServoSpeed, ServoInitACC);
        else if(SERVO_TYPE_SELECT == 2) st.WritePosEx(listID[activeNumInList], 0, rangeCtrl(activeServoSpeed,200,999)+1024, 0);
      }
      break;
    case 7:activeSpeed(100);break;
    case 8:activeSpeed(-100);break;
    case 9:servotoSet += 1;if(servotoSet > 250){servotoSet = 0;}break;
    case 10:servotoSet -= 1;if(servotoSet < 0){servotoSet = 0;}break;
    case 11:setMiddle(listID[activeNumInList]);break;
    case 12:setMode(listID[activeNumInList], 0);break;
    case 13:setMode(listID[activeNumInList], 3);break;
    case 14:SERIAL_FORWARDING = true;break;
    case 15:SERIAL_FORWARDING = false;break;
    case 16:setID(listID[activeNumInList], servotoSet);break;
    case 17:DEV_ROLE = 0;break;
    case 18:DEV_ROLE = 1;break;
    case 19:DEV_ROLE = 2;break;
    case 20:RAINBOW_STATUS = 1;break;
    case 21:RAINBOW_STATUS = 0;break;
  }
}

void handleRoot() { server.send(200, "text/html", index_html); }

void handleID() {
  if(!searchedStatus && searchFinished){
    String IDmessage = "ID:";
    for(int i = 0; i< searchNum; i++) IDmessage += String(listID[i]) + " ";
    server.send(200, "text/plane", IDmessage);
  }
  else if(searchedStatus) server.send(200, "text/plane", "Searching...");
}

void set_new_ID(){
  // USAGE: http://IP/set_id?id=1&new_id=5
  if /*(server.hasArg("id") && server.hasArg("new_id"))*/ (1) {
    int id = server.arg("id").toInt();
    int new_id = server.arg("new_id").toInt();

    // if(new_id > MAX_ID){MAX_ID = ID_set;}
      st.unLockEprom(id);
      st.writeByte(id, SMS_STS_ID, new_id);
      st.LockEprom(new_id);
    
    server.send(200, "text/plain", "OK: New ID set");
    Serial.println("New ID set successfully");
  } else {
    server.send(400, "text/plain", "Error: Missing current id or new id args");
    Serial.println("Failed to set new ID");
  }

}

void handleSTS() {
  String stsValue = "Active ID:" + String(listID[activeNumInList]);
  if(voltageRead[listID[activeNumInList]] != -1){
    stsValue += "  Position:" + String(posRead[listID[activeNumInList]]);
    if(DEV_ROLE == 0) stsValue += "<p>Device Mode: Normal";
    else if(DEV_ROLE == 1) stsValue += "<p>Device Mode: Leader";
    else if(DEV_ROLE == 2) stsValue += "<p>Device Mode: Follower";
    stsValue += "<p>Voltage:" + String(float(voltageRead[listID[activeNumInList]])/10);
    stsValue += "  Load:" + String(loadRead[listID[activeNumInList]]);
    stsValue += "<p>Speed:" + String(speedRead[listID[activeNumInList]]);
    stsValue += "  Temper:" + String(temperRead[listID[activeNumInList]]);
    stsValue += "<p>Speed Set:" + String(activeServoSpeed);
    stsValue += "<p>ID to Set:" + String(servotoSet);
    stsValue += "<p>Mode:";
    if(modeRead[listID[activeNumInList]] == 0) stsValue += "Servo Mode";
    else if(modeRead[listID[activeNumInList]] == 3) stsValue += "Motor Mode";

    if(Torque_List[activeNumInList]) stsValue += "<p>Torque On";
    else stsValue += "<p>Torque Off";
  }
  else stsValue += " FeedBack err";
  server.send(200, "text/plane", stsValue);
}

// ==========================================
// === MODIFIED SERVER SETUP              ===
// ==========================================

void webCtrlServer(){
    // Original Handles
    server.on("/", handleRoot);
    server.on("/readID", handleID);
    server.on("/set_id", set_new_ID);
    server.on("/readSTS", handleSTS);

    // NEW Python API Handles
    server.on("/move", handleMove);
    server.on("/torque", handleTorque);
    server.on("/mode", handleMode);      // <--- THIS IS THE FIX
    server.on("/feedback", handleFeedback);
    server.on("/multiturn", handleMultiTurn);
    server.on("/gripper", handleGripper);
     server.on("/calibrate", handleCalibrateZero);

    // Original Command Handler for Web Interface
    server.on("/cmd", [](){
      int cmdT = server.arg(0).toInt();
      int cmdI = server.arg(1).toInt();
      activeID(cmdI); // Simplified fallback for some calls
      if(cmdT == 1) activeCtrl(cmdI);
      if(cmdT == 9) searchCmd = true;
      server.send(200, "text/plain", "OK");
    });

  server.begin();
  Serial.println("Server Starts.");
}

void webServerSetup(){ 
  // --- Initialize the SG90 Servo ---
  gripperServo.setPeriodHertz(50);             // Standard 50Hz for SG90
  gripperServo.attach(13, 500, 2400); // Standard pulse width
  gripperServo.write(90); 

  webCtrlServer(); 
  }

void getMAC(){
  WiFi.mode(WIFI_AP_STA);
  MAC_ADDRESS = WiFi.macAddress();
  Serial.print("MAC:"); Serial.println(WiFi.macAddress());
}

void getIP(){
  IP_ADDRESS = WiFi.localIP();
  Serial.print("IP:");
  Serial.println(WiFi.localIP());
}

void setAP(){
  WiFi.softAP(AP_SSID, AP_PWD);
  IPAddress myIP = WiFi.softAPIP();
  IP_ADDRESS = myIP;
  Serial.print("AP IP address: "); Serial.println(myIP);
  WIFI_MODE = 1;
}

void setSTA(){
  WIFI_MODE = 3;
  WiFi.begin(STA_SSID, STA_PWD);
  getIP();
}

void getWifiStatus(){
  if(WiFi.status() == WL_CONNECTED){
    WIFI_MODE = 2; getIP(); WIFI_RSSI = WiFi.RSSI();
  }
  else if(WiFi.status() == WL_CONNECTION_LOST && DEFAULT_WIFI_MODE == 2){
    WIFI_MODE = 3; WiFi.reconnect();
  }
}

void wifiInit(){
  DEV_ROLE  = DEFAULT_ROLE;
  WIFI_MODE = DEFAULT_WIFI_MODE;
  if(WIFI_MODE == 1) setAP();
  else if(WIFI_MODE == 2) setSTA();
}

void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("\r\nLast Packet Send Status:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
  if(DEV_ROLE == 2){
    memcpy(&myData, incomingData, sizeof(myData));
    myData.Spd_send = abs(myData.Spd_send);
    if(myData.Spd_send < 50) myData.Spd_send = 200;
    st.WritePosEx(myData.ID_send, myData.POS_send, abs(myData.Spd_send), 0);
  }
}

void espNowInit(){
  WiFi.mode(WIFI_STA);
  // if (esp_now_init() != ESP_OK) { Serial.println("Error initializing ESP-NOW"); return; }
  // esp_now_register_send_cb(OnDataSent);
  // esp_now_register_recv_cb(OnDataRecv);
  // esp_now_peer_info_t peerInfo;
  // memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  // peerInfo.channel = 0;  
  // peerInfo.encrypt = false;
  // if (esp_now_add_peer(&peerInfo) != ESP_OK){ Serial.println("Failed to add peer"); return; }
  // MAC_ADDRESS = WiFi.macAddress();
  // Serial.print("MAC:"); Serial.println(WiFi.macAddress());
}

// void espNowInit(){
//   // Set device as a Wi-Fi Station
//   WiFi.mode(WIFI_STA);

//   // Init ESP-NOW
//   if (esp_now_init() != ESP_OK) {
//     Serial.println("Error initializing ESP-NOW");
//     return;
//   }

//   // Once ESPNow is successfully Init, we will register for Send CB to
//   // get the status of Trasnmitted packet
//   esp_now_register_send_cb(OnDataSent);
//   esp_now_register_recv_cb(OnDataRecv);

//   // Register peer
//   esp_now_peer_info_t peerInfo;
//   memcpy(peerInfo.peer_addr, broadcastAddress, 6);
//   peerInfo.channel = 0;  
//   peerInfo.encrypt = false;
  
//   // Add peer        
//   if (esp_now_add_peer(&peerInfo) != ESP_OK){
//     Serial.println("Failed to add peer");
//     return;
//   }

//   MAC_ADDRESS = WiFi.macAddress();
//   Serial.print("MAC:");
//   Serial.println(WiFi.macAddress());
// }