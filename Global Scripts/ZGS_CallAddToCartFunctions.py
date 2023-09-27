import ZGS_VariantPricingConditions as ZGS_VariantPricingConditions
import ZGS_MarginsTotals as ZGS_MarginsTotals
import ZGS_Approvals as ZGS_Approvals
Trace.Write("Calling Add to Quote scripts")

ZGS_MarginsTotals.buildMargins(context)
ZGS_VariantPricingConditions.calculatePricing(context)
ZGS_Approvals.buildApproval(context)