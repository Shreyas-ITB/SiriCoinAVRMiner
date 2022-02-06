#include <ArduinoJson.h>

void setup()
{
  Serial.begin(115200);
  Serial.setTimeout(1);
  while(!Serial) {}
}

void loop()
{
  if(Serial.available() > 0){
      Run();
  }
}

String readString;

void Run() {
    char c = Serial.read();
    if (c == '*') {
      DynamicJsonDocument doc(1024);
      deserializeJson(doc, readString);
      serializeJson(doc["operation"], Serial);
    }  
    else {     
      readString += c;
    }
}  
