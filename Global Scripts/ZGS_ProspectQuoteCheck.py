############################
##  Check if we have a Prospect partnerfunctionkey on the quote
##  If we do, then lock the QuoteType field via RD customization
##  based on QuoteType_Default == BUD (locks quote)
##  Defect #1981
############################

hasSP = hasPRO = hasSH = False
for party in context.Quote.GetInvolvedParties():
    if party.PartnerFunctionKey == "SP": hasSP = True
    elif party.PartnerFunctionKey == "SH": hasSH = True
    elif party.PartnerFunctionKey == "PRO": hasPRO = True

if hasPRO and not hasSP and not hasSH:
    context.Quote.GetCustomField('ZQT_QuoteType_Default').Value = "BUD"
else:
    context.Quote.GetCustomField('ZQT_QuoteType_Default').Value = "STD"