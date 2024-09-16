import yfinance as yf
import pandas as pd
import numpy as np
import time
from requests.exceptions import HTTPError, RequestException

# List of stock tickers to analyze (You can expand this list or fetch from an index)
tickers = [
'A','AAL','AAPL','ABBV','ABM','ABNB','ABT','ACGL','ACN','ADBE','ADI','ADM','ADP','ADSK','ADX','AEE','AEO','AEP','AES','AFL','AGRO','AIG','AIZ','AJG','AKAM','AKO','ALB','ALGN','ALK','ALKS','ALL','ALLE','ALV','AMAT','AMCR','AMD','AME','AMGN','AMK','AMP','AMPH','AMT','AMWD','AMZN','ANET','ANSS','AON','AOS','APA','APD','APH','APLE','APTV','ARCC','ARE','ATO','AVB','AVGO','AVY','AWK','AX','AXON','AXP','AXS','AZO','BA','BAC','BALL','BAX','BBVA','BBWI','BBY','BDX','BEN','BF','BG','BIIB','BIO','BK','BKNG','BKR','BLDR','BLK','BLX','BMA','BMY','BR','BRK','BRO','BSX','BUR','BWA','BWMX','BX','BXP','C','CAAP','CAG','CAH','CAKE','CARR','CAT','CB','CBOE','CBRE','CBT','CCI','CCL','CCSI','CDNS','CDW','CE','CEE','CEG','CEPU','CF','CFG','CGBD','CHD','CHRW','CHTR','CHX','CI','CINF','CION','CL','CLS','CLX','CMBT','CMCSA','CME','CMG','CMI','CMS','CNC','CNO','CNP','COF','COO','COP','COR','COST','CPAY','CPB','CPRT','CPT','CRCT','CRL','CRM','CRWD','CSCO','CSGP','CSX','CTAS','CTLT','CTRA','CTSH','CTVA','CUBI','CVE','CVS','CVX','CZR','D','DAL','DAY','DD','DE','DECK','DFS','DG','DGX','DHI','DHR','DIS','DLR','DLTR','DNOW','DOC','DOLE','DOV','DOW','DPZ','DRI','DTE','DUK','DVA','DVN','DXCM','EA','EBAY','ECC','ECL','ED','EFT','EFX','EG','EIX','EL','ELV','EMBC','EMN','EMR','ENPH','ENS','EOG','EPAM','EQIX','EQR','EQT','ES','ESGR','ESS','ETG','ETN','ETR','ETSY','ETY','EVRG','EW','EXC','EXPD','EXPE','EXR','EZPW','F','FANG','FANH','FAST','FCT','FCX','FDS','FDX','FE','FFIV','FI','FICO','FIS','FITB','FMC','FNF','FOX','FOXA','FPH','FRT','FSK','FSLR','FTNT','FTV','GAM','GBDC','GBX','GD','GDDY','GE','GEHC','GEN','GEV','GGN','GILD','GIS','GL','GLW','GM','GNRC','GOOG','GOOGL','GPC','GPN','GRMN','GS','GWW','HAL','HAS','HBAN','HBB','HCA','HD','HES','HIG','HII','HLT','HMC','HOLX','HON','HPE','HPQ','HRL','HSIC','HST','HSY','HUBB','HUM','HWM','HY','IBM','ICE','IDCC','IDXX','IEX','IFF','IGA','IMMR','INCY','INTC','INTU','INVH','IP','IPG','IQV','IR','IRM','ISRG','ISSC','IT','ITW','IVZ','IX','J','JBHT','JBL','JCI','JILL','JKHY','JKS','JNJ','JNPR','JPM','JXN','K','KDP','KELYA','KEY','KEYS','KHC','KIM','KKR','KLAC','KMB','KMI','KMX','KNTK','KO','KR','KSPI','KVUE','L','LAUR','LDOS','LEN','LFT','LH','LHX','LIN','LKQ','LLY','LMT','LNT','LOB','LOW','LPG','LRCX','LRN','LTC','LULU','LUV','LVS','LW','LYB','LYG','LYV','MA','MAA','MAR','MAS','MCD','MCHP','MCI','MCK','MCO','MDLZ','MDT','MET','META','MFIC','MGM','MHK','MITT','MKC','MKTX','MLM','MLR','MMC','MMM','MNST','MO','MOH','MOS','MPC','MPV','MPWR','MRK','MRNA','MRO','MRX','MS','MSCI','MSFT','MSGE','MSI','MTB','MTCH','MTD','MU','MUFG','NCLH','NDAQ','NDSN','NE','NEE','NEM','NFLX','NGVC','NI','NKE','NMR','NOC','NOV','NOW','NPK','NRG','NSC','NTAP','NTRS','NUE','NVDA','NVR','NWS','NWSA','NXPI','NXT','O','ODC','ODFL','OKE','OMC','ON','OPI','OPRA','OPY','ORAN','ORCL','ORLY','OSK','OTIS','OXY','PAM','PANW','PARA','PAYC','PAYX','PCAR','PCG','PDS','PEG','PEP','PFE','PFG','PG','PGR','PH','PHM','PKG','PLD','PLYA','PM','PNC','PNR','PNW','PODD','POOL','PPC','PPG','PPL','PRU','PSA','PSX','PTC','PVH','PWR','PYPL','QCOM','QRVO','RCL','REG','REGN','REVG','RF','RGA','RJF','RL','RMD','ROCK','ROK','ROL','ROP','ROST','RSG','RTX','RVTY','SBAC','SBUX','SCHW','SCM','SENEA','SGU','SHW','SIG','SITC','SJM','SKWD','SLB','SLM','SLRC','SMCI','SNA','SNPS','SO','SOLV','SPG','SPGI','SPNT','SRE','STE','STLD','STT','STX','STZ','SUN','SUPV','SW','SWK','SWKS','SYF','SYK','SYY','T','TAP','TBBK','TDG','TDY','TECH','TEL','TER','TFC','TFX','TGT','THC','TIGR','TILE','TIMB','TJX','TKC','TLN','TM','TMO','TMUS','TPR','TRGP','TRIN','TRMB','TROW','TRP','TRV','TSCO','TSLA','TSN','TT','TTWO','TXN','TXT','TYL','TZOO','UAL','UBER','UDR','UHS','ULTA','UNH','UNP','UPS','URBN','URI','USB','UVE','V','VAL','VBNK','VC','VEL','VICI','VIRT','VIST','VLO','VLTO','VMC','VNOM','VOYA','VRSK','VRSN','VRTX','VST','VTR','VTRS','VVR','VZ','WAB','WAT','WBA','WBD','WDC','WEC','WELL','WES','WFC','WFRD','WM','WMB','WMT','WRB','WS','WST','WTW','WY','WYNN','XEL','XOM','XYF','XYL','YALA','YRD','YUM','YY','ZBH','ZBRA','ZGN','ZTS','ADS.DE','ADYEN.AS','AD.AS','AI.PA','AIR.PA','ALV.DE','ABIEBR','ASML.AS','CS.PA','BAS.DE','BAYN.DE','BBVA.MC','SAN.MC','BMW.DE','BNP.PA','BN.PA','DB1.DE','DHL.DE','DTE.DE','ENEL.MI','ENI.MI','EL.PA','RACE.MI','FLTR.L','RMS.PA','IBE.MC','ITX.MC','IFX.DE','INGA.AS','ISP.MI','KER.PA','OR.PA','MC.PA','MBG.DE','MUV2.DE','NOKIA.HE','NDA-FI.HE','RI.PA','PRX.AS','SAF.PA','SGO.PA','SAN.PA','SAP.DE','SU.PA','SIE.DE','STLAM.MI','TTE.PA','DG.PA','UCG.MI','VOW.DE','III.L','ADM.L','AAF.L','AAL.L','ANTO.L','AHT.L','ABF.L','AZN.L','AUTO.L','AV.L','BME.L','BA.L','BARC.L','BDEV.L','BEZ.L','BKG.L','BP.L','BATS.L','BT.A.L','BNZL.L','BRBY.L','CNA.L','CCH.L','CPG.L','CTEC.L','CRDA.L','DARK.L','DCC.L','DGE.L','DPLM.L','EDV.L','ENT.L','EZJ.L','EXPN.L','FCIT.L','FRAS.L','FRES.L','GLEN.L','GSK.L','HLN.L','HLMA.L','HL.L','HIK.L','HWDN.L','HSBA.L','IHG.L','IMI.L','IMB.L','INF.L','ICG.L','IAG.L','ITRK.L','JD.L','KGF.L','LAND.L','LGEN.L','LLOY.L','LMP.L','LSEG.L','MNG.L','MKS.L','MRO.L','MNDI.L','NG.L','NWG.L','NXT.L','PSON.L','PSH.L','PSN.L','PHNX.L','PRU.L','RKT.L','REL.L','RTO.L','RMV.L','RIO.L','RR.L','SGE.L','SBRY.L','SDR.L','SMT.L','SGRO.L','SVT.L','SHEL.L','SMDS.L','SMIN.L','SN.L','SPX.L','SSE.L','STAN.L','TW.L','TSCO.L','ULVR.L','UU.L','UTG.L','VTY.L','VOD.L','WEIR.L','WTB.L','WPP.L','1209.HK','2020.HK','9618.HK','0267.HK','0002.HK','9633.HK','2688.HK','2015.HK','0003.HK','1038.HK','0017.HK','1398.HK','0012.HK','1109.HK','0883.HK','0669.HK','0027.HK','2319.HK','9988.HK','0101.HK','6690.HK','2269.HK','3690.HK','1810.HK','1044.HK','2628.HK','2331.HK','1093.HK','0992.HK','0241.HK','NVDA','QRVO','NOVA','YMM','APP','IMMR','PAY','AXTI','INST','SMCI','IDCC','APLD','KSPI','IONQ','KVYO','CRDO','NXT','GRND','RBRK','GTLB','BTCM','SPCE','CHPT','UP','OPEN','PTON','SABR','CRSR','FIGS','QRTEA','CLNE','VIR','EVGO','EAF','AHT','BORR','WOOF','EBON','HIPO','BIG','AMWL','GPRO','HLX','BFLY','REAL','PACB','CCO','CENX','IRWD','CWH','ZUO','SFIX','SSRM','BYND','WW','COMM','RXT','STEM','CCRN','PRPL','TTI','SLQT','KRNY','KPTI','CURV','UPWK','HPP','COOK','VNET','RDFN','JELD','LMND','PD','FREY','CNDT','DHC','EGHT','IHRT','TDUP','CRBU','WWW','IRBT','SPWH','LGF-A','CSIQ','HLIT','MRSN','LYEL','MXCT','EVC','FLWS','TSE','CRNC','HAIN','NAUT','TLYS','SEDG','HOPE','LUNG','SWIM','GTN','BNED','LGF-B','CMAX','SNBR','NVCR','EHTH','RAIL','DESP','IGR','TREE','TILE','VREX','ZYXI','BAND','HZO','ADCT','CARS','ZVIA','ADPT','BLND','GBIO','DLX','ACCD','CANG','VLRS','CTKB','CCCC','SSP','ANVS','WSBC','VIOT','LDI','SBGI','UIS','AMSC','CDXS','SSTK','ILPT','AMRC','SRI','HVT','PACK','ADTN','AKRO','BDTX','ARQT','SRG','NVRO','TBI','CIO','BMEA','XMTR','ARVN','SGHT','DCOM','CFFN','BRDG','HLLY','BUSE','ATHA','PRAA','QNST','MED','SNCY','STTK','MEI','LOB','APOG','TPC','SASR','CTRN','OCFC','CUBI','AOUT','TWI','GCO','ABSI','LKFN','NGVT','KLTR','AOSL','BLFY','QUAD','NBR','LAW','NINE','FFWM','TISI','HTZ','PFC','GLT','RYI','DLTH','ALGT','UVSP','BXC','BOOM','SCWX','NNBR','PNTG','HONE','CUTR','EFSC','GLUE','SQNS','AKYA','SAFE','STBA','KLXE','LXU','HAFC','CNOB','CNTA','AMTB','CPS','AMSWA','FFIC','MMI','APEI','CFB','MTRX','OPRA','LGO','LYTS','IBCP','TG','TTEC','XBIT','UFI','CLBK','HBNC','VVI','FARO','WSBF','MBWM','LCUT','ORN','FET','HUT','RCKY','PFBC','HBT','HTBI','PHAT','CSTE','CRMT','AGX','RBCAA','SRCE','BSRR','WASH','CTBI','PEBO','TSQ','LMNR','ALTG','MSBI','SOPH','NRC','THFF','BFST','SYBT','CARE','ULH','CCNE','PDS','MPX','RBB','FCBC','PGC','HOFT','MCB','WTBA','MLAB','MOFG','NGS','FISI','GSBC','USAP','BBU','CAC','PKOH','HBCP','MCBS','GEOS','EVA','FSTR','INBK','INZY','BCML','FNLC','FBIZ','AROW','SMBK','BARK','FSBC','VHI','NRIM','TWIN','BSVN','STRS','CCB','MYFW','EBTC','WRLD','ODC','SHBI','RRBI','PFIS','HOWL','PLPC','QRTEB','NBTX','CFFI','BPRN','ARBK','EVO','AHT-PF','AHT-PI','SES','AHT-PG','SPIR','QTI','ONIT','CCRD','IREN','CTRI','OPAD','ARHS','HUMA','DH','BKKT','WRBY','NYAX','BRCC','VATE','ONL','ACDC','CTNM','SSBK','ANRO','CIFR','TCBX','ALUR','EXAI','GREE','SOND','STEL','BBAI','BKSY','VCSA','WGS','EVEX','GETY','NXDT','SMR','HOUS','SLDP','SLRN','IBTA','FRGE','EMBC','IFIN','LFCR','OBK','EXFY','DOUG','LAB','TRML','KIND','SST','NRDY','VTYX','DTC','BBUC','MGX','BYON','TSAT','NIC','PL','FNA','NRGV','AMPS','CTV','AMPX','PKST','EVTL','SEAT','BIRD','WOLF','UPBD']

# Initialize lists to store the results
stocks_results = []
missing_data_tickers = []
rejected_stocks = []

# Define the delay between requests (in seconds)
REQUEST_DELAY = 0.0001  # Adjust based on the API rate limits

# Set volume threshold for "high volume" (adjust based on your needs)
VOLUME_THRESHOLD = 10000000  # Example: Exclude stocks with daily volume > 10M

def throttle_request():
    """Pause execution to throttle API requests."""
    time.sleep(REQUEST_DELAY)

def fetch_stock_data(ticker):
    """Fetch stock data using Yahoo Finance."""
    try:
        throttle_request()  # Throttle the request
        stock = yf.Ticker(ticker)
        # Attempt to fetch history with the preferred period
        try:
            history = stock.history(period="1y")
        except ValueError as e:
            print(f"{ticker}: Using fallback period due to error: {e}")
            history = stock.history(period="6mo")  # Fallback to 6 months if 1 year is not supported
        
        info = stock.info
        print(f"Successfully fetched data for {ticker}")
        return info, history
    except HTTPError as http_err:
        raise HTTPError(f"HTTP error occurred for {ticker}: {http_err}")
    except RequestException as req_err:
        raise RequestException(f"Request error occurred for {ticker}: {req_err}")
    except Exception as e:
        raise Exception(f"General error occurred for {ticker}: {e}")

def analyze_stock(ticker, stock_info, stock_history):
    """Analyze the stock based on financial and technical metrics."""
    reasons_for_rejection = []
    
    try:
        # Retrieve fundamental metrics
        name = stock_info.get('shortName', 'N/A')
        current_price = stock_info.get('currentPrice', 'N/A')
        industry = stock_info.get('industry', 'N/A')
        country = stock_info.get('country', 'N/A')
        sector = stock_info.get('sector', 'N/A')
        long_business_summary = stock_info.get('longBusinessSummary', 'N/A')
        trailing_pe = stock_info.get('trailingPE', 'N/A')
        peg_ratio = stock_info.get('pegRatio', 'N/A')
        ps_ratio = stock_info.get('priceToSalesTrailing12Months', 'N/A')
        roe = stock_info.get('returnOnEquity', 'N/A')
        profit_margin = stock_info.get('profitMargins', 'N/A')
        eps = stock_info.get('trailingEps', 'N/A')
        revenue_growth = stock_info.get('revenueGrowth', 'N/A')
        fifty_two_week_high = stock_info.get('fiftyTwoWeekHigh', 'N/A')
        fifty_two_week_low = stock_info.get('fiftyTwoWeekLow', 'N/A')
        overall_risk = stock_info.get('overallRisk', 'N/A')
        quick_ratio = stock_info.get('quickRatio', 'N/A')
        current_ratio = stock_info.get('currentRatio', 'N/A')

        # Exclude stocks with specific criteria, adding reasons for rejection
       # if current_price is None or (isinstance(current_price, (int, float)) and current_price > 5):
#            reasons_for_rejection.append("Current price > 75")
         #if trailing_pe is not None and isinstance(trailing_pe, (int, float)) and trailing_pe > 5:
         #    reasons_for_rejection.append("Trailing P/E > 5")
        if peg_ratio is not None and isinstance(peg_ratio, (int, float)) and peg_ratio > 1.25:
            reasons_for_rejection.append("PEG Ratio > 1.3")
        if quick_ratio is not None and isinstance(quick_ratio, (int, float)) and quick_ratio < 0.7:
            reasons_for_rejection.append("Quick Ratio < 0.5")
        if current_ratio is not None and isinstance(current_ratio, (int, float)) and current_ratio < 0.7:
            reasons_for_rejection.append("Current Ratio < 0.5")
        if eps is not None and isinstance(eps, (int, float)) and eps < -5:
            reasons_for_rejection.append("EPS < -15")
        if revenue_growth is not None and isinstance(revenue_growth, (int, float)) and revenue_growth < -0.10:
            reasons_for_rejection.append("Revenue Growth < -15%")
        if profit_margin is not None and isinstance(profit_margin, (int, float)) and profit_margin < -0.10:
            reasons_for_rejection.append("Profit Margin < -15%")
        
        # If any reason for rejection is found, reject the stock
        if reasons_for_rejection:
            rejected_stocks.append({
                'Ticker': ticker,
                'Name': name,
                'Reasons for Rejection': ', '.join(reasons_for_rejection)
            })
            print(f"Excluding {ticker}: {', '.join(reasons_for_rejection)}")
            return
        
        # Calculate technical metrics
        close_prices = stock_history['Close'].ffill().bfill()
        if close_prices.empty:
            raise ValueError(f"No historical price data for {ticker}.")
        
        # Relative Strength Index (RSI)
        delta = close_prices.diff(1)
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]

        # Moving Averages
        ma_50 = close_prices.rolling(window=50).mean().iloc[-1]
        ma_200 = close_prices.rolling(window=200).mean().iloc[-1]

        # Volume Analysis
        volume = stock_history['Volume'].iloc[-1]

        # Exclude high volume stocks
        #if volume > VOLUME_THRESHOLD:
#            rejected_stocks.append({
#                'Ticker': ticker,
#                'Name': name,
#                'Reasons for Rejection': "High Volume"
#            })
#            print(f"Excluding {ticker} due to high volume: {volume}")
#            return
        
        # Check if 50-day MA > 200-day MA
        ma_50_vs_ma_200 = ma_50 > ma_200

        # Store the results
        stocks_results.append({
            'Ticker': ticker,
            'Name': name,
            'Current Price': round(current_price, 4) if current_price != 'N/A' else 'N/A',
            'Industry': industry,
            'Country': country,
            'Sector': sector,
            'Trailing P/E': round(trailing_pe, 4) if trailing_pe != 'N/A' else 'N/A',
            'PEG Ratio': round(peg_ratio, 4) if peg_ratio != 'N/A' else 'N/A',
            'P/S Ratio': round(ps_ratio, 4) if ps_ratio != 'N/A' else 'N/A',
            'ROE (%)': round(roe * 100, 2) if roe != 'N/A' else 'N/A',
            'Profit Margin (%)': round(profit_margin * 100, 2) if profit_margin != 'N/A' else 'N/A',
            'EPS': round(eps, 4) if eps != 'N/A' else 'N/A',
            'Revenue Growth (%)': round(revenue_growth * 100, 2) if revenue_growth != 'N/A' else 'N/A',
            '52-Week High': round(fifty_two_week_high, 4) if fifty_two_week_high != 'N/A' else 'N/A',
            '52-Week Low': round(fifty_two_week_low, 4) if fifty_two_week_low != 'N/A' else 'N/A',
            'Overall Risk': overall_risk,
            'Quick Ratio': round(quick_ratio, 4) if quick_ratio != 'N/A' else 'N/A',
            'Current Ratio': round(current_ratio, 4) if current_ratio != 'N/A' else 'N/A',
            'RSI': round(rsi, 2),
            '50-day MA > 200-day MA': ma_50_vs_ma_200,
            'Volume': volume,
            'Long Business Summary': long_business_summary
        })

    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}")
        missing_data_tickers.append({
            'Ticker': ticker,
            'Error': str(e)
        })

for ticker in tickers:
    try:
        stock_info, stock_history = fetch_stock_data(ticker)
        analyze_stock(ticker, stock_info, stock_history)
    except Exception as e:
        print(f"Failed to process {ticker}: {str(e)}")
        missing_data_tickers.append({
            'Ticker': ticker,
            'Error': str(e)
        })

# Convert lists to DataFrames
df_results = pd.DataFrame(stocks_results)
df_missing = pd.DataFrame(missing_data_tickers)
df_rejected = pd.DataFrame(rejected_stocks)

# Save the results to an Excel file with separate sheets
with pd.ExcelWriter('stocks_analysis_results.xlsx') as writer:
    df_results.to_excel(writer, sheet_name='Analysis Results', index=False)
    df_missing.to_excel(writer, sheet_name='Missing Data', index=False)
    df_rejected.to_excel(writer, sheet_name='Rejected Stocks', index=False)

print("Analysis completed and saved to 'stocks_analysis_results.xlsx'.")
