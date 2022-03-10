/*
  

    ░██████╗██╗██████╗░██╗░░░░░░░█████╗░░█████╗░██╗███╗░░██╗
    ██╔════╝██║██╔══██╗██║░░░░░░██╔══██╗██╔══██╗██║████╗░██║
    ╚█████╗░██║██████╔╝██║█████╗██║░░╚═╝██║░░██║██║██╔██╗██║
    ░╚═══██╗██║██╔══██╗██║╚════╝██║░░██╗██║░░██║██║██║╚████║
    ██████╔╝██║██║░░██║██║░░░░░░╚█████╔╝╚█████╔╝██║██║░╚███║
    ╚═════╝░╚═╝╚═╝░░╚═╝╚═╝░░░░░░░╚════╝░░╚════╝░╚═╝╚═╝░░╚══╝
  Official code for Arduino boards                 version 1.3
  
  Siri-Coin Team & Community 2021-2022 © MIT Licensed
  https://siricoin.tech
  https://github.com/Shreyas-ITB/SiriCoinAVRMiner
  If you don't know where to start, visit official website and click on
  the Whitepaper button Have fun mining!
*/

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
