//+------------------------------------------------------------------+
//| GTI_MT5_ReadOnly_Bridge.mq5                                      |
//| GTI-AI-V2 -> Render MT5 Read-Only Market Data Bridge             |
//|                                                                  |
//| SAFETY: This EA contains NO trading functions.                   |
//| It does NOT open, modify, or close orders.                       |
//+------------------------------------------------------------------+
#property strict
#property version   "1.0"

input string BridgeURL        = "https://gti-ai-v2-mt5-bridge-api.onrender.com";
input string BridgeSecret    = "";
input string BridgeSymbol    = "XAUUSD";
input int    CandleCount     = 200;
input int    SendIntervalSec = 10;

datetime last_send = 0;

//-------------------------------------------------------------------
// Escape JSON string characters
//-------------------------------------------------------------------
string JsonEscape(string value)
{
   StringReplace(value, "\\", "\\\\");
   StringReplace(value, "\"", "\\\"");
   StringReplace(value, "\r", "\\r");
   StringReplace(value, "\n", "\\n");
   return value;
}

//-------------------------------------------------------------------
// Convert timeframe to string
//-------------------------------------------------------------------
string TFName(ENUM_TIMEFRAMES tf)
{
   switch(tf)
   {
      case PERIOD_M1:  return "M1";
      case PERIOD_M5:  return "M5";
      case PERIOD_M15: return "M15";
      case PERIOD_H1:  return "H1";
      case PERIOD_H4:  return "H4";
   }

   return "UNKNOWN";
}

//-------------------------------------------------------------------
// Build candle JSON array from CLOSED candles only
//-------------------------------------------------------------------
string BuildCandles(string symbol, ENUM_TIMEFRAMES tf, int count)
{
   MqlRates rates[];

   int copied = CopyRates(
      symbol,
      tf,
      1,
      count,
      rates
   );

   if(copied <= 0)
      return "[]";

   ArraySetAsSeries(rates, false);

   string json = "[";

   for(int i = 0; i < copied; i++)
   {
      if(i > 0)
         json += ",";

      json += "{";
      json += "\"time\":"   + IntegerToString((long)rates[i].time) + ",";
      json += "\"open\":"   + DoubleToString(rates[i].open, 8) + ",";
      json += "\"high\":"   + DoubleToString(rates[i].high, 8) + ",";
      json += "\"low\":"    + DoubleToString(rates[i].low, 8) + ",";
      json += "\"close\":"  + DoubleToString(rates[i].close, 8) + ",";
      json += "\"tick_volume\":" + IntegerToString((long)rates[i].tick_volume);
      json += "}";
   }

   json += "]";

   return json;
}

//-------------------------------------------------------------------
// Send snapshot to Render Bridge
//-------------------------------------------------------------------
bool SendSnapshot()
{
   string symbol = BridgeSymbol;

   if(!SymbolSelect(symbol, true))
   {
      Print("GTI BRIDGE: SymbolSelect failed for ", symbol);
      return false;
   }

   MqlTick tick;

   if(!SymbolInfoTick(symbol, tick))
   {
      Print("GTI BRIDGE: SymbolInfoTick failed for ", symbol);
      return false;
   }

   if(tick.bid <= 0 || tick.ask <= 0 || tick.ask < tick.bid)
   {
      Print("GTI BRIDGE: Invalid Bid/Ask");
      return false;
   }

   string body = "{";

   body += "\"symbol\":\"" + JsonEscape(symbol) + "\",";

   body += "\"market\":{";

   body += "\"H4\":"  + BuildCandles(symbol, PERIOD_H4,  CandleCount) + ",";
   body += "\"H1\":"  + BuildCandles(symbol, PERIOD_H1,  CandleCount) + ",";
   body += "\"M15\":" + BuildCandles(symbol, PERIOD_M15, CandleCount) + ",";
   body += "\"M5\":"  + BuildCandles(symbol, PERIOD_M5,  CandleCount) + ",";
   body += "\"M1\":"  + BuildCandles(symbol, PERIOD_M1,  CandleCount);

   body += "},";

   body += "\"price\":{";
   body += "\"bid\":" + DoubleToString(tick.bid, 8) + ",";
   body += "\"ask\":" + DoubleToString(tick.ask, 8);
   body += "},";

   body += "\"source_time\":" + IntegerToString((long)TimeCurrent());

   body += "}";

   string url = StringTrimRight(BridgeURL);

   if(StringSubstr(url, StringLen(url)-1, 1) == "/")
      url = StringSubstr(url, 0, StringLen(url)-1);

   url += "/ingest";

   string headers =
      "Authorization: Bearer " + BridgeSecret + "\r\n"
      "Content-Type: application/json\r\n"
      "Accept: application/json\r\n";

   uchar data[];
   uchar result[];
   string result_headers;

   StringToCharArray(body, data, 0, StringLen(body), CP_UTF8);

   ResetLastError();

   int status = WebRequest(
      "POST",
      url,
      headers,
      15000,
      data,
      result,
      result_headers
   );

   if(status == -1)
   {
      Print(
         "GTI BRIDGE: WebRequest failed. Error=",
         GetLastError()
      );
      return false;
   }

   string response = CharArrayToString(result, 0, -1, CP_UTF8);

   if(status < 200 || status >= 300)
   {
      Print(
         "GTI BRIDGE: HTTP ",
         status,
         " Response=",
         response
      );
      return false;
   }

   Print(
      "GTI BRIDGE: Snapshot sent successfully. HTTP ",
      status
   );

   return true;
}

//-------------------------------------------------------------------
// Expert initialization
//-------------------------------------------------------------------
int OnInit()
{
   Print("==============================================");
   Print(" GTI-AI-V2 READ-ONLY MT5 BRIDGE");
   Print("==============================================");
   Print("Symbol: ", BridgeSymbol);
   Print("Mode: READ-ONLY");
   Print("Trading: DISABLED");
   Print("OrderSend: NOT USED");
   Print("Bridge: ", BridgeURL);

   if(BridgeSecret == "")
   {
      Print("WARNING: BridgeSecret is empty.");
      Print("EA will not be able to authenticate with Render.");
   }

   EventSetTimer(MathMax(1, SendIntervalSec));

   return INIT_SUCCEEDED;
}

//-------------------------------------------------------------------
// Timer
//-------------------------------------------------------------------
void OnTimer()
{
   SendSnapshot();
}

//-------------------------------------------------------------------
// Tick
//-------------------------------------------------------------------
void OnTick()
{
   // Intentionally empty.
   // This EA does not trade.
}

//-------------------------------------------------------------------
// Expert deinitialization
//-------------------------------------------------------------------
void OnDeinit(const int reason)
{
   EventKillTimer();

   Print("GTI BRIDGE: EA stopped. No trading actions were performed.");
}
//+------------------------------------------------------------------+
