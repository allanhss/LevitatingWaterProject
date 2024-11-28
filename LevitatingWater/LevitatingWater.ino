// Pino do PWM controlado pelo Timer1
const int pwmPin = 9;  // O Timer1 controla os pinos 9 e 10

// Variáveis para frequência e duty cycle
float frequency = 15;   // Frequência padrão inicial (em Hz)
float dutyCycle = 0;  // Duty cycle padrão inicial (em %)

// Tempo limite para comunicação serial (em milissegundos)
unsigned long lastCommunicationTime = 0;
const unsigned long timeout = 5000;  // 5 segundos

// Função para configurar o PWM com a frequência e duty cycle
void setPWMTimer1(float frequency, float dutyCycle) {
  int prescaler;
  long topValue;
  
  // Limite de frequência (mínima e máxima)
  if (frequency < 1) frequency = 1;  // Frequência mínima de 1 Hz
  if (frequency > 50) frequency = 50;  // Frequência máxima de 50 Hz

  // Determina o prescaler adequado com base na frequência desejada
  if (frequency >= 1 && frequency <= 31) {
    prescaler = 1024;  // Prescaler de 1024 para frequências baixas (1Hz a 31Hz)
    topValue = (16000000 / (2 * prescaler * frequency)) - 1;
    TCCR1B = (1 << WGM13) | (1 << WGM12) | (1 << CS12) | (1 << CS10);  // Fast PWM com prescaler 1024
  } else if (frequency > 31 && frequency <= 50) {
    prescaler = 64;  // Prescaler de 64 para frequências mais altas (32Hz a 50Hz)
    topValue = (16000000 / (2 * prescaler * frequency)) - 1;
    TCCR1B = (1 << WGM13) | (1 << WGM12) | (1 << CS11) | (1 << CS10);  // Fast PWM com prescaler 64
  }

  // Configura o Timer1 para Fast PWM com o valor de TOP
  TCCR1A = (1 << WGM11) | (1 << COM1A1);  // Modo PWM rápido, limpa OC1A quando atinge o comparador
  
  ICR1 = topValue;  // Define o valor do TOP no Timer1
  
  // Calcula o valor de OCR1A para o duty cycle
  OCR1A = (dutyCycle == 0) ? 0 : (dutyCycle == 100) ? topValue : (int)(topValue * (dutyCycle / 100.0));
}

void setup() {
  // Inicializa a comunicação serial
  Serial.begin(9600);
  
  // Configura o pino do PWM como saída
  pinMode(pwmPin, OUTPUT);
  
  // Inicializa o Timer1 com os valores padrão de frequência e duty cycle (15 Hz e 100%)
  setPWMTimer1(frequency, dutyCycle);
  
  // Imprime mensagem de inicialização
  Serial.println("Esperando dados de frequência e duty cycle via Serial...");
}

void loop() {
  // Verifica se há dados disponíveis na porta serial
  if (Serial.available() > 0) {
    // Lê os dados da serial
    String input = Serial.readStringUntil('\n');
    
    // Divide a string recebida em frequência e duty cycle
    int commaIndex = input.indexOf(',');
    if (commaIndex > 0) {
      String freqStr = input.substring(0, commaIndex);
      String dutyStr = input.substring(commaIndex + 1);

      // Converte as strings para float
      float newFrequency = freqStr.toFloat();
      float newDutyCycle = dutyStr.toFloat();

      // Limita a frequência à faixa permitida (1 Hz a 50 Hz)
      if (newFrequency >= 1 && newFrequency <= 50) {
        frequency = newFrequency;
      }

      // Limita o duty cycle à faixa permitida (0% a 100%)
      if (newDutyCycle >= 0 && newDutyCycle <= 100) {
        dutyCycle = newDutyCycle;
      }

      // Imprime os valores recebidos para verificação
      Serial.print("Frequência recebida: ");
      Serial.print(frequency);
      Serial.println(" Hz");

      Serial.print("Duty cycle recebido: ");
      Serial.print(dutyCycle);
      Serial.println(" %");

      // Atualiza o tempo da última comunicação
      lastCommunicationTime = millis();
      
      // Aplica os novos valores de frequência e duty cycle
      setPWMTimer1(frequency, dutyCycle);
    }
  }

  // Verifica se a comunicação serial foi recebida nos últimos 5 segundos
  if (millis() - lastCommunicationTime > timeout) {
    // Sem comunicação recente, manter os valores atuais (não aplicar mudanças)
    Serial.println("Sem comunicação recente. Mantendo os valores atuais.");
  
    // Reinicia o tempo da última comunicação para evitar repetição de mensagens
    lastCommunicationTime = millis();
  }
}
