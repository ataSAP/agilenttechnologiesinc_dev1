import ZGS_VariantPricingConditions as ZGS_VariantPricingConditions
import ZGS_MarginsTotals as ZGS_MarginsTotals
import ZGS_Approvals as ZGS_Approvals

context.Quote.Calculate("Quantity")
ZGS_MarginsTotals.buildMargins(context)
ZGS_VariantPricingConditions.calculatePricing(context)
ZGS_Approvals.buildApproval(context)