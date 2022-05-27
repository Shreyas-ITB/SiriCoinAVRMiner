/*
 * Minerador Siri-Coin
 * Desenvolvido por Albério Lima (Brazil)
 * 04-2022
*/

#pragma GCC optimize ("-Ofast")

#include "sph_keccak.h"

#if defined(ARDUINO_ARCH_STM32F1) && (F_CPU==128000000L)
  #define SERIAL Serial1
#else
  #define SERIAL Serial
#endif

/* Variáveis públicas */
unsigned char uchar_bRoot[64];
size_t size_bRoot = 0;
unsigned char uchar_target[32];
uint64_t uint64_target = 0;
unsigned char resultado[32];
unsigned long nonce = 0;
unsigned long tempo = 0;
unsigned long tempoTrabalho = 30;
String dadosRecebidos = "";

#define LED_ON LOW

void setup() {
  SERIAL.begin(115200);
  pinMode( LED_BUILTIN, OUTPUT );
  digitalWrite( LED_BUILTIN, !LED_ON );
}

void loop() {
  yield();
  /* Recebe trabalho pela serial */
  boolean trabalhoRecebido = recebeTrabalho();

  /* Executa o trabalho */
  if (trabalhoRecebido) {
    trabalhoRecebido = false;
    
    /* pula zeros a esqueda do nonce */
    size_bRoot += 28;               
    
    nonce = 0;    
    tempo = 0;
    unsigned long tfinal = millis() + ( tempoTrabalho * 1000UL );
    unsigned long timeStart = micros();
    max_micros_elapsed(timeStart, 0);
    while (millis()<tfinal) {
      /* Coloca nonce*/
      nonce++;      
      uchar_bRoot[size_bRoot]=(unsigned char)(nonce>>24);
      uchar_bRoot[size_bRoot+1]=(unsigned char)(nonce>>16);
      uchar_bRoot[size_bRoot+2]=(unsigned char)(nonce>>8);
      uchar_bRoot[size_bRoot+3]=(unsigned char)(nonce);      
      
      sph_keccak_context ctx;        
      sph_keccak256_init(&ctx);  
      sph_keccak256(&ctx, uchar_bRoot, size_bRoot+4);
      sph_keccak256_close(&ctx, resultado);
      
      if ( hashToUint64(resultado) < uint64_target ) {        
        tempo = micros() - timeStart;
        SERIAL.print(nonce);
        SERIAL.print(",");
        SERIAL.print(tempo);
        SERIAL.print(",");
        printHex(resultado,32);        
        SERIAL.print("\n");
        tfinal = millis();
      }
      if (max_micros_elapsed(micros(), 1000000)) {
        yield();
      }
    }  
    if (tempo == 0 ){
      tempo = micros() - timeStart;
      SERIAL.print(nonce);
      SERIAL.print(",");
      SERIAL.print(tempo);
      SERIAL.print(",0x0\n");    
    }
  }
}

bool max_micros_elapsed(unsigned long current, unsigned long max_elapsed) {
  static unsigned long _start = 0;

  if ((current - _start) > max_elapsed) {
    _start = current;
    return true;
  }
  return false;
}

void printHex( unsigned char* d, size_t ln ) {
  uint8_t i = 0;
  SERIAL.print("0x");
  while (i < ln ) {
    if (d[i] < 0x10) {
      SERIAL.print("0");
    }
    SERIAL.print(String(d[i], HEX));
    i++;
  }  
}

uint64_t hashToUint64( const unsigned char* d ) {
  uint64_t u = 0;
  u += (uint64_t)d[0]<<56;
  u += (uint64_t)d[1]<<48;
  u += (uint64_t)d[2]<<40;
  u += (uint64_t)d[3]<<32;
  u += (uint64_t)d[4]<<24;
  u += (uint64_t)d[5]<<16;
  u += (uint64_t)d[6]<<8;
  u += (uint64_t)d[7];      
  return u;
}

boolean recebeTrabalho() {
  if (!SERIAL.available()) {
    return false;
  }
  while (SERIAL.available()) {
    char c = SERIAL.read();
    if ( c == '\n' ) {
      if ( dadosRecebidos.length() < 32 ) {
        dadosRecebidos = "";
        return false;
      }
      digitalWrite( LED_BUILTIN, LED_ON );
      delay(100);
      digitalWrite( LED_BUILTIN, !LED_ON );
      
      /* Decodifica bRoot */
      String bRoot = "";
      bRoot = dadosRecebidos.substring(0, dadosRecebidos.indexOf(','));
      bRoot = bRoot.substring(2);
      size_bRoot = (bRoot.length() / 2);
      memset(uchar_bRoot, 0, sizeof(uchar_bRoot));
      for (size_t i = 0, j = 0; j < size_bRoot; i += 2, j++) {
        uchar_bRoot[j] = (bRoot[i] % 32 + 9) % 25 * 16 + (bRoot[i + 1] % 32 + 9) % 25;
      }

      /* Decodifica target */
      dadosRecebidos = dadosRecebidos.substring(dadosRecebidos.indexOf(',') + 1);
      String target = "";
      target = dadosRecebidos.substring(0, dadosRecebidos.indexOf(','));
      target = target.substring(2);
      while (target.length() < bRoot.length() ){
        target = "0" + target;
      }
      memset(uchar_target, 0, 32);
      size_t j = 32 - (target.length() / 2);
      for ( size_t i = 0; j < 32; i += 2, j++) {
        uchar_target[j] = (target[i] % 32 + 9) % 25 * 16 + (target[i + 1] % 32 + 9) % 25;      
      }
      uint64_target = hashToUint64(uchar_target);

      /* Pega tempo de trabalho */
      dadosRecebidos = dadosRecebidos.substring(dadosRecebidos.indexOf(',') + 1);
      if ( dadosRecebidos.toInt() > 0 ) {
        tempoTrabalho = (unsigned long)dadosRecebidos.toInt();
      }
      /* Reinicia dados a receber */
      dadosRecebidos = "";
      return true;
    } else {
      dadosRecebidos += c;
    }
  }
  return false;
}
