Trace.Write("START-ZMA_MaterialFieldsMapping")
import ZGS_ConvertCurrency as ZGS_ConvertCurrency

def getFloat(val):
    try: x = float(val)
    except: x = 0.00
    return x

def get_parts(quote_items):
    part_list_array = []
    #quote_items = context.Quote.GetAllItems()
    for item in quote_items:
        item["ZPR_Completed"] = "Y"
        part_list_array.append(item.PartNumber)
    part_list_string = "'" + "','".join(str(x) for x in part_list_array) + "'"
    return part_list_string

def checkUoM(data,quote_items,product):
    for item in quote_items:
        for item_material in data:
            if item.PartNumber == item_material.MaterialNumber:
                Trace.Write("FOUND MATCH")
                tableUoM = item_material.SalesUnit
                productUoM = item.GetUnitOfMeasure("ListPrice")
                Trace.Write("TABLE UNIT: {0} - Product Unit: {1}".format(tableUoM,productUoM))
                if (tableUoM != productUoM) and (tableUoM != '') and (tableUoM is not None):
                    product.UnitOfMeasure = tableUoM
                Trace.Write("New UoM {0}".format(product.UnitOfMeasure))
                #
                break

def assign_simple(columns,data,quote_items):
    for col in columns:
        for item in quote_items:
            for item_material in data:
                if item.PartNumber == item_material.MaterialNumber:
                    #Trace.Write("FOUND MATCH")
                    item[columns[col]] = getattr(item_material,col)
                    break

def item_category(quote_items):
    T184 = SqlHelper.GetList("SELECT ItemCatGrp,HigherLevelItemCat,ItemCat FROM ZMA_ItemCategoryDetermination")
    TVAP = SqlHelper.GetList("SELECT ItemCategory,PricingRel,OrderQty FROM ZMA_ItemCategoryData")
    higher_level = [""]
    for item in quote_items:
        level = item.RolledUpQuoteItem.count(".")
        #Trace.Write("level is " + str(level) + "length is " + str(len(higher_level)))
        if level + 2 > len(higher_level):
            higher_level.append("")
        for cat_row in T184:
            if cat_row.ItemCatGrp == item["ZPR_ItemCategoryGroup"] and cat_row.HigherLevelItemCat == higher_level[level]:
                item["ZPR_ItemCategory"] = cat_row.ItemCat
                higher_level[level+1] = cat_row.ItemCat
                for t_row in TVAP:
                    if t_row.ItemCategory == cat_row.ItemCat:
                        item["ZPR_PricingRel"] = t_row.PricingRel
                        item["ZPR_QtyRestricted"] = t_row.OrderQty

def get_plants(quote_items):
    all_plants = []
    for item in quote_items:
        #Trace.Write("Material = {0}  Plant = {1}".format(item.PartNumber,item["ZPR_Plant"]))
        if item["ZPR_Plant"] not in all_plants:
            all_plants.append(item["ZPR_Plant"])
    plant_string = "'"+"','".join(all_plants)+"'"
    return (plant_string)

def assign_plant_data(quote_items,data):
    for item in quote_items:
        if item.ParentItemId == 0:
            parent_item = context.Quote.GetItemByItemId(item.Id)
        for item_material in data:
            if item.PartNumber == item_material.MaterialNumber and item["ZPR_Plant"] == item_material.Plant:
                item_cost = getFloat(item_material.StandardPrice)
                quote_currency = context.Quote.SelectedMarket.CurrencyCode
                if quote_currency != "USD":
                    item_cost = ZGS_ConvertCurrency.convert_currency(item_material.StandardPrice,"USD",quote_currency)
                item["ZPR_Cost"] = item_cost
                item["ZPR_ProfitCenter"] = item_material.ProfitCenter
                Trace.Write("Profit Center:" + str(item_material.ProfitCenter.lstrip("0")))
                prod_fam = SqlHelper.GetFirst("SELECT ProductFamily from ZMA_ProductFamily WHERE ProfitCenter = '{0}'".format(item_material.ProfitCenter.lstrip("0")))
                if prod_fam:
                    Trace.Write("Product Family:" + str(prod_fam.ProductFamily))
                    item["ZMA_ProductFamily"] = prod_fam.ProductFamily
                    thresholdData = SqlHelper.GetList("Select * from ZMA_MarginThreshold WHERE SubRegion = '{0}' AND ProductFamily = '{1}'".format("North America",prod_fam.ProductFamily))
                    for marginItem in thresholdData:
                        approvalLevel = "ZPR_" + marginItem.ApprovalLevel.replace(" ","") + "Margin"
                        item[approvalLevel] = getFloat(marginItem.MarginSub)

## {columnName : fieldName}
material_cols = {
                 'ProductHierarchy':'ZPR_ProductHierarchy',
                 'MaterialGroup':'ZPR_MaterialGroup',
                 'GrossWeight':'ZPR_GrossWeight',
                 'NetWeight':'ZPR_NetWeight',
                 'WeightUnit':'ZPR_WeightUnit',
                 'PL':'ZPR_Division',
    			 'GSA':'ZPR_GSA_NA',
    			 'SalesText':'ZMA_SalesText'
                 }
sales_cols = {
              'ItemCategoryGroup':'ZPR_ItemCategoryGroup',
              'MaterialPricingGroup':'ZPR_MaterialPricingGroup',
              'FreightShippingCode':'ZPR_FreightShippingCode',
              'DeliveringPlant':'ZPR_Plant',
    		  'MaterialStatus':'ZPR_MaterialStatus'
              }
plant_cols = {
              'ProfitCenter':'ZPR_ProfitCenter',
              'StandardPrice':'Cost'
              }

#Trace.Write("In field mapping")
#Trace.Write("PRODUCTUOMIS : {0}".format(Product.UnitOfMeasure))
#Trace.Write("CONTEXT IS" + str(dir(context)))
#context.Product.UnitOfMeasure = "BT"
sales_org = context.Quote.SelectedMarket.Code
quote_items = context.Items
part_list = get_parts(quote_items)
item_material_data = SqlHelper.GetList("SELECT * FROM ZMA_MATERIALFIELDS WHERE MaterialNumber IN ({0})".format(part_list))
item_sales_data = SqlHelper.GetList("SELECT * FROM ZMA_MATERIALSALES WHERE SalesOrganization = '{0}' AND MaterialNumber IN ({1})".format(sales_org,part_list))
checkUoM(item_sales_data,quote_items,context.Product)
assign_simple(material_cols,item_material_data,quote_items)
assign_simple(sales_cols,item_sales_data,quote_items)
item_category(quote_items)
plant_string = get_plants(quote_items)
#Trace.Write("platnstrr" + plant_string)
item_plant_data = SqlHelper.GetList("SELECT * FROM ZMA_MATERIALPLANT WHERE MaterialNumber IN ({0}) AND Plant IN ({1})".format(part_list,plant_string))
#Trace.Write(item_plant_data)
assign_plant_data(quote_items,item_plant_data)