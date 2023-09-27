#Script Name:APPOSTSATR
import sys
import datetime
import SYSEXTCALL
try:
	Parameter = SqlHelper.GetFirst("SELECT QUERY_CRITERIA_1 FROM SYDBQS (NOLOCK) WHERE QUERY_NAME = 'SELECT' ")	
	Parameter1 = SqlHelper.GetFirst("SELECT QUERY_CRITERIA_1 FROM SYDBQS (NOLOCK) WHERE QUERY_NAME = 'UPD' ")
	Parameter2 = SqlHelper.GetFirst("SELECT QUERY_CRITERIA_1 FROM SYDBQS (NOLOCK) WHERE QUERY_NAME = 'DEL' ")
	
	#webclient = System.Net.WebClient()
	#webclient.Headers[System.Net.HttpRequestHeader.ContentType] = "application/json"
	#webclient.Headers[System.Net.HttpRequestHeader.Authorization] ="Basic UzAwMjA5NzM1NDI6QkhDY3BpQDEyMw==" #"Basic UzAwMjA5NzM1NDI6SmsxMjMxMjAyMSE="
	#requestURL = "https://hanadb.c-673c570.kyma.shoot.live.k8s-hana.ondemand.com"
	#response2= webclient.UploadString(requestURL,'{"query":"select TerritoryID,Region,Country,SalesForce,SalesOrg,Area,AreaDescription,AreaManagerName,District,DistrictDescription,DistrictManagerName,StartDate,Enddate,SalesRole,SalesChannel,MRRoleCode,PayEvent,TerritoryStatus,TerritoryRole,BUSSINESSORGANIZATION from TRUVIS where territorystatus=\'A\'"}')
	schema=SYSEXTCALL.HanaDbHelper().DBSchema()
	Getcls=SYSEXTCALL.HanaDbHelper()				
	response2=Getcls.getList({"query":'select TerritoryID,Region,Country,SalesForce,SalesOrg,Area,AreaDescription,AreaManagerName,District,DistrictDescription,DistrictManagerName,StartDate,Enddate,SalesRole,SalesChannel,MRRoleCode,PayEvent,TerritoryStatus,TerritoryRole,BUSSINESSORGANIZATION from '+schema+'TRUVIS where territorystatus=\'A\''})
	#response2=response2.replace("null",'""')
	#response2=eval(response2)
	Trace.Write(str(response2))
	
	
			
	a=response2
	for items in a:
		for col in ['TERRITORYID','REGION','COUNTRY','SALESFORCE','SALESORG','AREA','AREADESCRIPTION','AREAMANAGERNAME','AREAMANAGERID','DISTRICT','DISTRICTDESCRIPTION','DISTRICTMANAGERNAME','DISTRICTMANAGERID','STARTDATE','ENDDATE','SALESROLE','SALESCHANNEL','MRROLECODE','PAYEVENT','TERRITORYSTATUS','TERRITORYROLE','BUSSINESSORGANIZATION']:
			if col not in items:
				items[col]=''
		primaryQueryItems = SqlHelper.GetFirst( ""+ str(Parameter.QUERY_CRITERIA_1)+ " APTRAP_INBOUND (TerritoryID,Region,Country,SalesForce,SalesOrg,Area,AreaDescription,AreaManagerName,AreaManagerID,District,DistrictDescription,DistrictManagerName,DistrictManagerID,StartDate,Enddate,SalesRole,SalesChannel,MRRoleCode,PayEvent,TerritoryStatus,TerritoryRole,BUSINESS_GROUP) select ''"+items['TERRITORYID']+ "'',''"+items['REGION']+ "'',''"+items['COUNTRY']+ "'',''"+items['SALESFORCE']+ "'',''"+items['SALESORG']+ "'',''"+items['AREA']+ "'',''"+items['AREADESCRIPTION']+ "'',''"+items['AREAMANAGERNAME']+ "'',''"+items['AREAMANAGERID']+ "'',''"+items['DISTRICT']+ "'',''"+items['DISTRICTDESCRIPTION']+ "'',''"+items['DISTRICTMANAGERNAME']+ "'',''"+items['DISTRICTMANAGERID']+ "'',''"+items['STARTDATE']+ "'',''"+items['ENDDATE']+ "'',''"+items['SALESROLE']+ "'',''"+items['SALESCHANNEL']+ "'',''"+items['MRROLECODE']+ "'',''"+items['PAYEVENT']+ "'',''"+items['TERRITORYSTATUS']+ "'',''"+items['TERRITORYROLE']+ "'',''"+items['BUSSINESSORGANIZATION']+ "'''")
		
			
	#Level 10 Update Starts
	UpdateQueryItems = SqlHelper.GetFirst(
	""
	+ str(Parameter1.QUERY_CRITERIA_1)
	+ " aptrap SET aptrap.CpqTableEntryModifiedBy = ''"
	+ str(User.Id)
	+"'',aptrap.CpqTableEntryDateModified = GetDate(),aptrap.APPROVAL_LEVEL=''LEVEL 10'',aptrap.APPROVAL_LEVEL_NAME=aptrap_inbound.DistrictManagerName,aptrap.APPROVAL_TERRITORY_ID=aptrap_inbound.TerritoryID,aptrap.DELEGATION_END=CONVERT(DATE,aptrap_inbound.Enddate),aptrap.DELEGATION_START=CONVERT(DATE,aptrap_inbound.StartDate),aptrap.REGION=aptrap_inbound.Region,aptrap.SALES_FORCE=aptrap_inbound.SalesForce,aptrap.PARREGION_RECORD_ID=saregn.REGION_RECORD_ID,aptrap.COUNTRY=aptrap_inbound.Country,aptrap.COUNTRY_RECORD_ID=sactry.COUNTRY_RECORD_ID,aptrap.SALESORG_ID=aptrap_inbound.SalesOrg,aptrap.SALESORG_RECORD_ID=sasorg.SALESORG_RECORD_ID,aptrap.LOCATION_ID=aptrap_inbound.District,aptrap.LOCATION_DESCRIPTION=aptrap_inbound.DistrictDescription,aptrap.SALES_CHANNEL=aptrap_inbound.SalesChannel,aptrap.APPROVAL_TERRITORY_STATUS=aptrap_inbound.TerritoryStatus,aptrap.APPROVAL_TERRITORY_ROLE=aptrap_inbound.TerritoryRole,aptrap.BUSINESS_GROUP=aptrap_inbound.BUSINESS_GROUP from APTRAP_INBOUND aptrap_inbound left join SAREGN saregn on saregn.REGION=aptrap_inbound.REGION left join SACTRY sactry on sactry.Country=aptrap_inbound.Country left join SASORG sasorg on SASORG.SalesOrg_Id=aptrap_inbound.SalesOrg join APTRAP aptrap on aptrap.APPROVAL_TERRITORY_ID=aptrap_inbound.TerritoryID and aptrap.APPROVAL_LEVEL=''LEVEL 10'' where isnull(Integration_Status,'''')='''''")
	
	#Level 10 Insert Starts
	primaryQueryItems = SqlHelper.GetFirst(
	""
	+ str(Parameter.QUERY_CRITERIA_1)
	+" APTRAP (approval_level,approval_level_name,approval_territory_id,delegation_end,delegation_start,region,sales_force,parregion_record_id,country,country_record_id,salesorg_id,salesorg_record_id,location_id,location_description,sales_channel,approval_territory_status,approval_territory_role,BUSINESS_GROUP) select A.* from( select distinct ''LEVEL 10'' as approval_level,aptrap_inbound.districtmanagername,aptrap_inbound.territoryid,CONVERT(  date,aptrap_inbound.enddate) as delegation_end,CONVERT(date,aptrap_inbound.startdate) as delegation_start,aptrap_inbound.region,aptrap_inbound.salesforce,saregn.region_record_id,aptrap_inbound.country,sactry.country_record_id,aptrap_inbound.salesorg,sasorg.salesorg_record_id,aptrap_inbound.district,aptrap_inbound.districtdescription,aptrap_inbound.saleschannel,aptrap_inbound.territorystatus,aptrap_inbound.territoryrole,aptrap_inbound.BUSINESS_GROUP from APTRAP_INBOUND aptrap_inbound left join SAREGN saregn on saregn.REGION=aptrap_inbound.REGION left join SACTRY sactry on sactry.Country=aptrap_inbound.Country left join SASORG sasorg on SASORG.SalesOrg_Id=aptrap_inbound.SalesOrg where isnull(aptrap_inbound.Integration_Status,'''')='''')A left join APTRAP aptrap on aptrap.APPROVAL_TERRITORY_ID=A.TerritoryID and aptrap.APPROVAL_LEVEL=''LEVEL 10'' where aptrap.APPROVAL_TERRITORY_ID is null'")


	#Level 20 Update Starts
	UpdateQueryItems = SqlHelper.GetFirst(
	""
	+ str(Parameter1.QUERY_CRITERIA_1)
	+ " aptrap SET aptrap.CpqTableEntryModifiedBy = ''"
	+ str(User.Id)
	+"'',aptrap.CpqTableEntryDateModified = GetDate(),aptrap.APPROVAL_LEVEL=''LEVEL 20'',aptrap.APPROVAL_LEVEL_NAME=aptrap_inbound.AreaManagerName,aptrap.APPROVAL_TERRITORY_ID=aptrap_inbound.TerritoryID,aptrap.DELEGATION_END=CONVERT(DATE,aptrap_inbound.Enddate),aptrap.DELEGATION_START=CONVERT(DATE,aptrap_inbound.StartDate),aptrap.REGION=aptrap_inbound.Region,aptrap.SALES_FORCE=aptrap_inbound.SalesForce,aptrap.PARREGION_RECORD_ID=saregn.REGION_RECORD_ID,aptrap.COUNTRY=aptrap_inbound.Country,aptrap.COUNTRY_RECORD_ID=sactry.COUNTRY_RECORD_ID,aptrap.SALESORG_ID=aptrap_inbound.SalesOrg,aptrap.SALESORG_RECORD_ID=sasorg.SALESORG_RECORD_ID,aptrap.LOCATION_ID=aptrap_inbound.Area,aptrap.LOCATION_DESCRIPTION=aptrap_inbound.AreaDescription,aptrap.SALES_CHANNEL=aptrap_inbound.SalesChannel,aptrap.APPROVAL_TERRITORY_STATUS=aptrap_inbound.TerritoryStatus,aptrap.APPROVAL_TERRITORY_ROLE=aptrap_inbound.TerritoryRole,aptrap.BUSINESS_GROUP=aptrap_inbound.BUSINESS_GROUP from APTRAP_INBOUND aptrap_inbound left join SAREGN saregn on saregn.REGION=aptrap_inbound.REGION left join SACTRY sactry on sactry.Country=aptrap_inbound.Country left join SASORG sasorg on SASORG.SalesOrg_Id=aptrap_inbound.SalesOrg join APTRAP aptrap on aptrap.APPROVAL_TERRITORY_ID=aptrap_inbound.TerritoryID and aptrap.APPROVAL_LEVEL=''LEVEL 20'' where isnull(Integration_Status,'''')='''''")
	
	
	#Level 20 Insert Starts
	primaryQueryItems = SqlHelper.GetFirst(
	""
	+ str(Parameter.QUERY_CRITERIA_1)
	+" APTRAP (approval_level,approval_level_name,approval_territory_id,delegation_end,delegation_start,region,sales_force,parregion_record_id,country,country_record_id,salesorg_id,salesorg_record_id,location_id,location_description,sales_channel,approval_territory_status,approval_territory_role,BUSINESS_GROUP) select A.* from( select distinct ''LEVEL 20'' as approval_level,aptrap_inbound.AreaManagerName,aptrap_inbound.territoryid,CONVERT(  date,aptrap_inbound.enddate) as delegation_end,CONVERT(date,aptrap_inbound.startdate) as delegation_start,aptrap_inbound.region,aptrap_inbound.salesforce,saregn.region_record_id,aptrap_inbound.country,sactry.country_record_id,aptrap_inbound.salesorg,sasorg.salesorg_record_id,aptrap_inbound.Area,aptrap_inbound.AreaDescription,aptrap_inbound.saleschannel,aptrap_inbound.territorystatus,aptrap_inbound.territoryrole,aptrap_inbound.BUSINESS_GROUP from APTRAP_INBOUND aptrap_inbound left join SAREGN saregn on saregn.REGION=aptrap_inbound.REGION left join SACTRY sactry on sactry.Country=aptrap_inbound.Country left join SASORG sasorg on SASORG.SalesOrg_Id=aptrap_inbound.SalesOrg where isnull(aptrap_inbound.Integration_Status,'''')='''')A left join APTRAP aptrap on aptrap.APPROVAL_TERRITORY_ID=A.TerritoryID and aptrap.APPROVAL_LEVEL=''LEVEL 20'' where aptrap.APPROVAL_TERRITORY_ID is null'")
	
	UpdateQueryItems = SqlHelper.GetFirst(
	""
	+ str(Parameter1.QUERY_CRITERIA_1)
	+ " aptrap_inbound SET aptrap_inbound.Integration_Status = ''uploaded'' from aptrap_inbound where isnull(aptrap_inbound.Integration_Status,'''')='''' '")
	
	ApiResponse = ApiResponseFactory.JsonResponse({"Response": [{"Status": "200", "Message": "Data Loaded Succesfully"}]})
		

except:
	ApiResponse = ApiResponseFactory.JsonResponse({"Response": [{"Status": "400", "Message": str(sys.exc_info()[1])}]})