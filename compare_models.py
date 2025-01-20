from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    Boolean,
    JSON,
    Float,
    LargeBinary,
)
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime


Base = declarative_base()


# BaseModel
class BaseModel(Base):
    __abstract__ = True
    created_date = Column(DateTime, default=datetime.now(), nullable=False)


# Tenant Model
class Tenant(BaseModel):
    __tablename__ = "tenants"
    tenant_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    additional_attributes = Column(JSON, default={})

    users = relationship("User", back_populates="tenant")
    organizations = relationship("Organization", back_populates="tenant")
    roles = relationship("Role", back_populates="tenant")
    permissions = relationship("Permission", back_populates="tenant")
    global_roles = relationship("GlobalRole", back_populates="tenant")
    integrations = relationship("Integration", back_populates="tenant")
    document_repositories = relationship("DocumentRepository", back_populates="tenant")
    notifications = relationship("Notification", back_populates="tenant")


# User Model
class User(BaseModel):
    __tablename__ = "users"
    user_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    display_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    department = Column(String(100), nullable=True)
    last_login_date = Column(DateTime, nullable=False)
    additional_attributes = Column(JSON, default={})

    tenant = relationship("Tenant", back_populates="users")
    identity_mappings = relationship("UserIdentityMapping", back_populates="user")
    org_unit_users = relationship("OrgUnitUser", back_populates="user")
    global_user_roles = relationship("GlobalUserRole", back_populates="user")


# UserIdentityMapping Model
class UserIdentityMapping(BaseModel):
    __tablename__ = "user_identity_mappings"
    mapping_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID, ForeignKey("users.user_id"), nullable=False)
    provider_name = Column(String(255), nullable=False)
    external_user_id = Column(String(255), nullable=False)
    last_sync_date = Column(DateTime, nullable=False)
    additional_attributes = Column(JSON, default={})

    user = relationship("User", back_populates="identity_mappings")


# Organization Model
class Organization(BaseModel):
    __tablename__ = "organizations"
    organization_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    name = Column(String(255), nullable=False)
    industry = Column(String(255), nullable=False)
    additional_attributes = Column(JSON, default={})

    tenant = relationship("Tenant", back_populates="organizations")
    org_units = relationship("OrgUnit", back_populates="organization")


# OrgUnit Model
class OrgUnit(BaseModel):
    __tablename__ = "org_units"
    org_unit_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(
        PG_UUID, ForeignKey("organizations.organization_id"), nullable=False
    )
    parent_org_unit_id = Column(
        PG_UUID, ForeignKey("org_units.org_unit_id"), nullable=True
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    additional_attributes = Column(JSON, default={})

    organization = relationship("Organization", back_populates="org_units")
    parent_org_unit = relationship("OrgUnit", remote_side=[org_unit_id])
    org_unit_users = relationship("OrgUnitUser", back_populates="org_unit")


# Permission Model
class Permission(BaseModel):
    __tablename__ = "permissions"
    permission_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    tenant = relationship("Tenant", back_populates="permissions")
    roles = relationship(
        "Role", secondary="role_permissions", back_populates="permissions"
    )
    global_roles = relationship(
        "GlobalRole", secondary="global_role_permissions", back_populates="permissions"
    )


# Role Model
class Role(BaseModel):
    __tablename__ = "roles"
    role_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    additional_attributes = Column(JSON, default={})

    tenant = relationship("Tenant", back_populates="roles")
    permissions = relationship(
        "Permission", secondary="role_permissions", back_populates="roles"
    )
    org_unit_users = relationship("OrgUnitUser", back_populates="role")


# RolePermission association table
class RolePermission(Base):
    __tablename__ = "role_permissions"
    role_id = Column(PG_UUID, ForeignKey("roles.role_id"), primary_key=True)
    permission_id = Column(
        PG_UUID, ForeignKey("permissions.permission_id"), primary_key=True
    )


# OrgUnitUser Model
class OrgUnitUser(BaseModel):
    __tablename__ = "org_unit_users"
    org_unit_user_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID, ForeignKey("users.user_id"), nullable=False)
    org_unit_id = Column(PG_UUID, ForeignKey("org_units.org_unit_id"), nullable=False)
    role_id = Column(PG_UUID, ForeignKey("roles.role_id"), nullable=False)
    assigned_date = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="org_unit_users")
    org_unit = relationship("OrgUnit", back_populates="org_unit_users")
    role = relationship("Role", back_populates="org_unit_users")


# GlobalUserRole Model
class GlobalUserRole(Base):
    __tablename__ = "global_user_roles"
    global_user_role_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID, ForeignKey("users.user_id"), nullable=False)
    global_role_id = Column(
        PG_UUID, ForeignKey("global_roles.global_role_id"), nullable=False
    )

    user = relationship("User", back_populates="global_user_roles")
    global_role = relationship("GlobalRole", back_populates="global_user_roles")


# Tender Model
class Tender(BaseModel):
    __tablename__ = "tenders"
    tender_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    org_unit_id = Column(PG_UUID, ForeignKey("org_units.org_unit_id"), nullable=False)
    organization_id = Column(
        PG_UUID, ForeignKey("organizations.organization_id"), nullable=False
    )
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    title = Column(String(255), nullable=False)
    tender_status_value_id = Column(PG_UUID, nullable=False)
    created_by_user_id = Column(PG_UUID, nullable=False)
    approved_date = Column(DateTime, nullable=True)
    tender_type_value_id = Column(PG_UUID, nullable=False)
    external_tender_id = Column(String(255), nullable=False)
    external_portal_name = Column(String(255), nullable=False)
    specification = Column(JSON, default={})
    criteria = Column(JSON, default={})
    integration_id = Column(PG_UUID, nullable=True)

    # Relationships
    org_unit = relationship("OrgUnit", back_populates="tenders")
    organization = relationship("Organization", back_populates="tenders")
    tenant = relationship("Tenant", back_populates="tenders")
    documents = relationship(
        "Document", secondary="tender_documents", back_populates="tenders"
    )
    evaluation_stages = relationship(
        "EvaluationStage",
        secondary="tender_evaluation_stages",
        back_populates="tenders",
    )
    bids = relationship("Bid", secondary="tender_bids", back_populates="tenders")

    def __str__(self):
        return self.title


# TenderDocument Model
class TenderDocument(BaseModel):
    __tablename__ = "tender_documents"
    document_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tender_id = Column(PG_UUID, ForeignKey("tenders.tender_id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    content = Column(LargeBinary, nullable=False)
    uploaded_date = Column(DateTime, nullable=False)
    document_source_value_id = Column(PG_UUID, nullable=False)
    external_document_id = Column(String(255), nullable=False)
    external_portal_name = Column(String(255), nullable=False)
    document_repository_id = Column(PG_UUID, nullable=False)

    # Relationship
    tender = relationship("Tender", back_populates="documents")

    def __str__(self):
        return self.file_name


# TenderSpecification Model
class TenderSpecification(BaseModel):
    __tablename__ = "tender_specifications"
    specification_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tender_id = Column(PG_UUID, ForeignKey("tenders.tender_id"), nullable=False)
    details = Column(Text, nullable=False)
    generated_date = Column(DateTime, nullable=False)
    additional_attributes = Column(JSON, default={})

    tender = relationship("Tender", back_populates="specifications")

    # def __repr__(self):
    #     return f"Specification for {self.tender.title}"


# Bid Model
class Bid(BaseModel):
    __tablename__ = "bids"
    bid_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tender_id = Column(PG_UUID, ForeignKey("tenders.tender_id"), nullable=False)
    bidder_id = Column(PG_UUID, nullable=False)
    submission_date = Column(DateTime, nullable=False)
    bid_status_value_id = Column(PG_UUID, nullable=False)
    additional_attributes = Column(JSON, default={})
    tender = relationship("Tender", back_populates="bids")
    bid_documents = relationship("BidDocument", back_populates="bid")
    evaluation_results = relationship("EvaluationResult", back_populates="bid")

    # def __str__(self):
    #     return f"Bid for {self.tender.title}"


# BidDocument Model
class BidDocument(BaseModel):
    __tablename__ = "bid_documents"
    document_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    bid_id = Column(PG_UUID, ForeignKey("bids.bid_id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    content = Column(LargeBinary, nullable=False)
    uploaded_date = Column(DateTime, nullable=False)
    document_source_value_id = Column(PG_UUID, nullable=False)
    external_document_id = Column(String(255), nullable=False)
    external_portal_name = Column(String(255), nullable=False)
    document_repository_id = Column(PG_UUID, nullable=False)

    bid = relationship("Bid", back_populates="bid_documents")

    def __str__(self):
        return self.file_name


# Bidder Model
class Bidder(BaseModel):
    __tablename__ = "bidders"
    bidder_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    name = Column(String(255), nullable=False)
    contact_info = Column(Text, nullable=False)
    additional_attributes = Column(JSON, default={})

    tenant = relationship("Tenant", back_populates="bidders")
    bids = relationship("Bid", back_populates="bidder")

    def __str__(self):
        return self.name


# EvaluationCriteria Model
class EvaluationCriteria(BaseModel):
    __tablename__ = "evaluation_criteria"
    criteria_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tender_id = Column(PG_UUID, ForeignKey("tenders.tender_id"), nullable=False)
    criteria_details = Column(Text, nullable=False)
    generated_date = Column(DateTime, nullable=False)
    evaluation_method_id = Column(PG_UUID, nullable=False)
    additional_attributes = Column(JSON, default={})

    tender = relationship("Tender", back_populates="evaluation_criteria")
    evaluation_method = relationship("EvaluationMethod", back_populates="criteria_list")

    # def __str__(self):
    #     return f"Evaluation Criteria for {self.tender.title}"


# EvaluationResult Model
class EvaluationResult(BaseModel):
    __tablename__ = "evaluation_results"
    result_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    bid_id = Column(PG_UUID, ForeignKey("bids.bid_id"), nullable=False)
    stage_id = Column(PG_UUID, nullable=False)
    category_id = Column(PG_UUID, nullable=False)
    criterion_id = Column(PG_UUID, nullable=False)
    evaluation_outcome_value_id = Column(PG_UUID, nullable=False)
    score = Column(Float, nullable=False)
    comments = Column(Text, nullable=False)
    additional_attributes = Column(JSON, default={})

    bid = relationship("Bid", back_populates="evaluation_results")

    # def __str__(self):
    #     return f"Evaluation Result for {self.bid}"


# EvaluationStage Model
class EvaluationStage(BaseModel):
    __tablename__ = "evaluation_stages"
    stage_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tender_id = Column(PG_UUID, ForeignKey("tenders.tender_id"), nullable=False)
    stage_type_value_id = Column(PG_UUID, nullable=False)
    sequence = Column(Integer, nullable=False)
    additional_attributes = Column(JSON, default={})

    tender = relationship("Tender", back_populates="evaluation_stages")

    # def __str__(self):
    #     return f"Evaluation Stage for {self.tender.title}"


# EvaluationCategory Model
class EvaluationCategory(BaseModel):
    __tablename__ = "evaluation_categories"
    category_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    stage_id = Column(PG_UUID, ForeignKey("evaluation_stages.stage_id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    sequence = Column(Integer, nullable=False)
    additional_attributes = Column(JSON, default={})

    stage = relationship("EvaluationStage", back_populates="categories")

    def __str__(self):
        return self.name


# EvaluationCriterion Model
class EvaluationCriterion(BaseModel):
    __tablename__ = "evaluation_criterion"
    criterion_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    category_id = Column(
        PG_UUID, ForeignKey("evaluation_categories.category_id"), nullable=False
    )
    description = Column(Text, nullable=False)
    weightage = Column(Integer, nullable=False)
    is_mandatory = Column(Boolean, default=True)
    criteria_type_value_id = Column(PG_UUID, nullable=False)
    sequence = Column(Integer, nullable=False)
    additional_attributes = Column(JSON, default={})

    category = relationship("EvaluationCategory", back_populates="criteria_list")

    def __str__(self):
        return self.description


# EvaluationMethod Model
class EvaluationMethod(BaseModel):
    __tablename__ = "evaluation_methods"
    evaluation_method_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    name = Column(String(255), nullable=False)
    technical_weightage = Column(Float, nullable=False)
    commercial_weightage = Column(Float, nullable=False)
    formula_or_notes = Column(Text, nullable=False)
    additional_attributes = Column(JSON, default={})

    tenant = relationship("Tenant", back_populates="evaluation_methods")

    def __str__(self):
        return self.name


# ReferenceType Model
class ReferenceType(BaseModel):
    __tablename__ = "reference_types"
    reference_type_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    def __str__(self):
        return self.name


# ReferenceValue Model
class ReferenceValue(BaseModel):
    __tablename__ = "reference_values"
    reference_value_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    reference_type_id = Column(
        PG_UUID, ForeignKey("reference_types.reference_type_id"), nullable=False
    )
    value = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    sort_order = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    additional_attributes = Column(JSON, default={})

    reference_type = relationship("ReferenceType", back_populates="reference_values")

    # def __str__(self):
    #     pass


# GlobalRole Model
class GlobalRole(BaseModel):
    __tablename__ = "global_roles"
    global_role_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    permissions = relationship(
        "Permission", secondary="global_role_permissions", back_populates="global_roles"
    )

    tenant = relationship("Tenant", back_populates="global_roles")

    def __str__(self):
        return self.name


# Integration Model
class Integration(BaseModel):
    __tablename__ = "integrations"
    integration_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    provider_name = Column(String(255), nullable=False)
    integration_type = Column(String(100), nullable=False)
    configuration_details = Column(JSON, default={})
    last_sync_date = Column(DateTime, nullable=False)

    tenant = relationship("Tenant", back_populates="integrations")

    def __str__(self):
        return self.provider_name


# DocumentRepository Model
class DocumentRepository(BaseModel):
    __tablename__ = "document_repositories"
    repository_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    provider_name = Column(String(255), nullable=False)
    repository_type = Column(String(100), nullable=False)
    configuration_details = Column(JSON, default={})

    tenant = relationship("Tenant", back_populates="document_repositories")

    def __str__(self):
        return self.provider_name


# Notification Model
class Notification(BaseModel):
    __tablename__ = "notifications"
    notification_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    notification_type_value_id = Column(PG_UUID, nullable=False)
    actor_user_id = Column(PG_UUID, nullable=False)
    content = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    additional_attributes = Column(JSON, default={})

    tenant = relationship("Tenant", back_populates="notifications")

    # def __str__(self):
    #     return f"Notification for {self.actor_user_id}"