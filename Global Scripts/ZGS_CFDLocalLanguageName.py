ER_email = ''
name  = ''
for party in context.Quote.GetInvolvedParties():
    if party.PartnerFunctionKey == "ER":
        ER_email = party.EmailAddress
        name = party.FirstName +" "+ party.LastName
        break

localName = SqlHelper.GetFirst("SELECT ucf.Content from Users JOIN UserCustomFields ucf ON ucf.userid = users.Id JOIN UserCustomFieldDefn ucfdef ON ucfdef.Id = ucf.CustomFieldId WHERE email = '{0}' AND ucfdef.Name = '{1}'".format(party.EmailAddress,"ZUF_LocalLanguage"))

context.Quote.GetCustomField("ZQT_CFDLocalLanguageName").Value = localName.Content if localName.Content != "" else name