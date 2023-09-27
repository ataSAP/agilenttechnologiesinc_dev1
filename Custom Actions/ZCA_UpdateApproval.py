approvalTypes = ["Sales","Finance"]
Trace.Write("Updating approvals")
for approvalType in approvalTypes:
    approvalTable = context.Quote.QuoteTables["ZQT_{0}_Approvals".format(approvalType)]
    approvalSet = 0
    firstRow = 1
    for row in approvalTable.Rows:
        if firstRow == 1 and row["Status"] == "Pending":
            row["Status"] = "In Progress"
            Trace.Write("Setting to in progress " + row["Approver"])
            break
        firstRow = 0
        if approvalSet == 1:
            row["Status"] = "In Progress"
            break
        if row["Approver"] == User.Email:
            row["Status"] = "Approved"
            approvalSet = 1
    #AllApprovers.Save()