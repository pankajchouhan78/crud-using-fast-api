from sqladmin import Admin, ModelView
from main import app
from models import *

admin = Admin(app, engine)

class TenantAdmin(ModelView, model=Tenant):
    column_list = (Tenant.tenant_id, Tenant.name, Tenant.description)


class OrganizationAdmin(ModelView, model=Organization):
    column_list = (
        Organization.organization_id,
        Organization.name,
        Organization.industry,
    )


class OrgUnitAdmin(ModelView, model=OrgUnit):
    column_list = (OrgUnit.org_unit_id, OrgUnit.name, OrgUnit.created_date)


class OrgUnitUserAdmin(ModelView, model=OrgUnitUser):
    column_list = (OrgUnitUser.org_unit_id, OrgUnitUser.created_date)


class ReferenceTypeAdmin(ModelView, model=ReferenceType):
    column_list = (ReferenceType.reference_type_id, ReferenceType.name)


class ReferenceValueAdmin(ModelView, model=ReferenceValue):
    column_list = (ReferenceValue.reference_value_id,)


class EvaluationMethodAdmin(ModelView, model=EvaluationMethod):
    column_list = (EvaluationMethod.created_date,)


class IntegrationAdmin(ModelView, model=Integration):
    column_list = (Integration.Integration_id, Integration.provider_name)


class DocumentRepositoryAdmin(ModelView, model=DocumentRepository):
    column_list = (DocumentRepository.created_date,)


class UserAdmin(ModelView, model=User):
    column_list = (User.display_name, User.email, User.tenant)


class UserIdentityMappingAdmin(ModelView, model=UserIdentityMapping):
    column_list = (UserIdentityMapping.user_id,)


class InvitationAdmin(ModelView, model=Invitation):
    column_list = (Invitation.invitation_id, Invitation.created_date)


class RoleAdmin(ModelView, model=Role):
    column_list = (Role.role_id, Role.name)


class PermissionAdmin(ModelView, model=Permission):
    column_list = (Permission.permission_id, Permission.name)


class GlobalRoleAdmin(ModelView, model=GlobalRole):
    column_list = (GlobalRole.global_role_id, GlobalRole.name)


class GlobalUserRoleAdmin(ModelView, model=GlobalUserRole):
    column_list = (GlobalUserRole.global_role_id,)


class TenderAdmin(ModelView, model=Tender):
    column_list = (Tender.title,)


class TenderSpecificationAdmin(ModelView, model=TenderSpecification):
    column_list = (
        TenderSpecification.specification_id,
        TenderSpecification.generated_date,
    )


class EvaluationCriteriaAdmin(ModelView, model=EvaluationCriteria):
    column_list = (EvaluationCriteria.criteria_id, EvaluationCriteria.created_date)


class EvaluationStageAdmin(ModelView, model=EvaluationStage):
    column_list = (EvaluationStage.criteria_id, EvaluationStage.created_date)


class EvaluationCategoryAdmin(ModelView, model=EvaluationCategory):
    column_list = (EvaluationCategory.category_id, EvaluationCategory.name)


class EvaluationCriterionAdmin(ModelView, model=EvaluationCriterion):
    column_list = (EvaluationCriterion.criterion_id, EvaluationCriterion.description)


class BidAdmin(ModelView, model=Bid):
    column_list = (Bid.bid_id, Bid.created_date)


class BidDocumentAdmin(ModelView, model=BidDocument):
    column_list = (BidDocument.document_id, BidDocument.created_date)


class BidderAdmin(ModelView, model=Bidder):
    column_list = (Bidder.bidder_id, Bidder.created_date)


class EvaluationResultAdmin(ModelView, model=EvaluationResult):
    column_list = (EvaluationResult.result_id, EvaluationResult.comments)


class TenderDocumentAdmin(ModelView, model=TenderDocument):
    column_list = (TenderDocument.document_id, TenderDocument.created_date)


class NotificationAdmin(ModelView, model=Notification):
    column_list = (Notification.notification_id, Notification.created_date)


class AuditLogAdmin(ModelView, model=AuditLog):
    column_list = (AuditLog.actor_user_id, AuditLog.created_date)


# Register the views with the admin interface
admin.add_view(TenantAdmin)
admin.add_view(OrganizationAdmin)
admin.add_view(OrgUnitAdmin)
admin.add_view(OrgUnitUserAdmin)
admin.add_view(ReferenceTypeAdmin)
admin.add_view(ReferenceValueAdmin)
admin.add_view(EvaluationMethodAdmin)
admin.add_view(IntegrationAdmin)
admin.add_view(DocumentRepositoryAdmin)
admin.add_view(UserAdmin)
admin.add_view(UserIdentityMappingAdmin)
admin.add_view(InvitationAdmin)
admin.add_view(RoleAdmin)
admin.add_view(PermissionAdmin)
admin.add_view(GlobalRoleAdmin)
admin.add_view(GlobalUserRoleAdmin)
admin.add_view(TenderAdmin)
admin.add_view(TenderSpecificationAdmin)
admin.add_view(EvaluationCriteriaAdmin)
admin.add_view(EvaluationStageAdmin)
admin.add_view(EvaluationCategoryAdmin)
admin.add_view(EvaluationCriterionAdmin)
admin.add_view(BidAdmin)
admin.add_view(BidDocumentAdmin)
admin.add_view(BidderAdmin)

# Register the views with the admin interface
admin.add_view(EvaluationResultAdmin)

admin.add_view(TenderDocumentAdmin)
admin.add_view(NotificationAdmin)
admin.add_view(AuditLogAdmin)
