import uuid
from datetime import datetime

from sqlalchemy import (create_engine, JSON, Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, LargeBinary, String, Table, Text, ARRAY, UniqueConstraint)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker


# Set the database connection details
DB_NAME = "db_test"
DB_USER = "postgres"
DB_USER_PASSWORD = "admin"
DB_HOST = "localhost"  # Replace with your actual host
DB_PORT = "5432"

# Create the PostgreSQL connection string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_USER_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the engine to connect to PostgreSQL
engine = create_engine(DATABASE_URL)

# Create the session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Set up the base class for declarative models
Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# BaseModel
class BaseModel(Base):
    __abstract__ = True
    created_date = Column(DateTime, default=datetime.now(), nullable=False)
    is_active = True


# Tenant Model
class Tenant(Base):
    __tablename__ = "tenants"

    tenant_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    additional_attributes = Column(JSON, default=dict)

    # Relationship
    users = relationship("User", back_populates="tenant")
    organizations = relationship('Organization', back_populates='tenant')
    permissions = relationship('Permission', back_populates='tenant')
    roles = relationship("Role", back_populates="tenant")
    tenders = relationship("Tender", back_populates="tenant")
    bidders = relationship("Bidder", back_populates="tenant")
    invitations = relationship("Invitation", back_populates="tenant")
    evaluation_method = relationship("EvaluationMethod", back_populates="tenant")
    global_role = relationship("GlobalRole", back_populates="tenant")
    document_repositories = relationship("DocumentRepository", back_populates="tenant")
    audit_log = relationship("AuditLog", back_populates="tenant")
    notifications = relationship("Notification", back_populates="tenant")
    
    
    def __str__(self):
        return f"<Tenant(name={self.name})>"

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

    # Relationship
    tenant = relationship("Tenant", back_populates="users")
    identity_mappings = relationship("UserIdentityMapping", back_populates="user")
    org_unit_users = relationship("OrgUnitUser", back_populates="user")
    global_user_roles = relationship("GlobalUserRole", back_populates="user")
    invitations = relationship("Invitation", back_populates="invited_by")     
    notifications = relationship("Notification", back_populates="user")
    audit_log = relationship("AuditLog", back_populates="actor_user", uselist=False)  # One-to-one relationship
    tender = relationship("Tender", back_populates="created_by_user")

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

    # Relationship
    tenant = relationship("Tenant", back_populates="organizations")
    org_units = relationship("OrgUnit", back_populates="organization")
    tenders = relationship("Tender", back_populates="organization")
    invitations = relationship("Invitation", back_populates="organization")

# OrgUnit Model - partial
class OrgUnit(BaseModel):
    __tablename__ = "org_units"

    org_unit_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(PG_UUID, ForeignKey("organizations.organization_id"), nullable=False)
    parent_org_unit_id = Column(PG_UUID, ForeignKey("org_units.org_unit_id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    additional_attributes = Column(JSON, default={})
    tenders = Column(ARRAY(String))
    org_unit_user = Column(ARRAY(String))

    organization = relationship("Organization", back_populates="org_units")
    org_unit_users = relationship("OrgUnitUser", back_populates="org_unit")
    tenders = relationship("Tender", back_populates="org_unit")
    # Self-referential relationship for parent-child OrgUnits
    parent_org_unit = relationship("OrgUnit", remote_side=[org_unit_id], backref="sub_units")

# Association Table for many-to-many relationship between Role and Permission
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", PG_UUID, ForeignKey("roles.role_id"), primary_key=True),
    Column("permission_id", PG_UUID, ForeignKey("permissions.permission_id"), primary_key=True),
)

# Association Table for many-to-many relationship between GlobalRole and Permission
global_role_permissions = Table(
    "global_role_permissions",
    Base.metadata,
    Column("global_role_id", PG_UUID, ForeignKey("global_roles.global_role_id"), primary_key=True),
    Column("permission_id", PG_UUID, ForeignKey("permissions.permission_id"), primary_key=True),
)


# Permission Model
class Permission(BaseModel):
    __tablename__ = "permissions"
    permission_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    tenant = relationship("Tenant", back_populates="permissions")
    # Many-to-many relationship with Role
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    # Many-to-many relationship with GlobalRole
    global_roles = relationship("GlobalRole", secondary="global_role_permissions", back_populates="permissions")


# Role Model
class Role(BaseModel):
    __tablename__ = "roles"
    role_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(ARRAY(String))
    additional_attributes = Column(JSON, default={})

    tenant = relationship("Tenant", back_populates="roles")
    # Many-to-many relationship with Permission
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")    
    org_unit_users = relationship("OrgUnitUser", back_populates="role")
    
    def __str__(self):
        return f"<Role(name={self.name})>"


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
    global_role_id = Column(PG_UUID, ForeignKey("global_roles.global_role_id"), nullable=False)

    user = relationship("User", back_populates="global_user_roles")
    global_role = relationship("GlobalRole", back_populates="global_user_roles")


# Tender Model
class Tender(BaseModel):
    __tablename__ = "tenders"
    tender_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    org_unit_id = Column(PG_UUID, ForeignKey("org_units.org_unit_id"), nullable=False)
    organization_id = Column(PG_UUID, ForeignKey("organizations.organization_id"), nullable=False)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    title = Column(String(255), nullable=False)
    tender_status_value_id = Column(PG_UUID, nullable=False)
    created_by_user_id = Column(PG_UUID, ForeignKey("users.user_id"), nullable=False)
    approved_date = Column(DateTime, nullable=True)
    tender_type_value_id = Column(PG_UUID, nullable=False)
    external_tender_id = Column(String(255), nullable=False)
    external_portal_name = Column(String(255), nullable=False)
    specification = Column(JSON, default={})
    criteria = Column(JSON, default={})
    document = Column(ARRAY(String))
    evaluation_stage = Column(ARRAY(String))
    bid = Column(ARRAY(String))
    integration_id = Column(PG_UUID, nullable=True)
    
    # Relationships
    org_unit = relationship("OrgUnit", back_populates="tenders")
    organization = relationship("Organization", back_populates="tenders")
    tenant = relationship("Tenant", back_populates="tenders")
    tender_specification = relationship("TenderSpecification", back_populates="tender", uselist=False)  # One-to-one
    documents = relationship("TenderDocument", back_populates="tender")
    bid = relationship("Bid", back_populates="tender")
    evaluation_stages = relationship("EvaluationStage", back_populates="tender")
    evaluation_criteria = relationship("EvaluationCriteria", back_populates="tender", uselist=False)  # One-to-one
    created_by_user = relationship("User", back_populates="tender")

    
    def __str__(self):
        return self.title


# TenderSpecification Model
class TenderSpecification(BaseModel):
    __tablename__ = "tender_specifications"
    specification_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tender_id = Column(PG_UUID, ForeignKey("tenders.tender_id", ondelete="CASCADE"), nullable=False, unique=True,)  # Unique constraint for one-to-one
    details = Column(Text, nullable=False)
    generated_date = Column(DateTime, nullable=False)
    additional_attributes = Column(JSON, default={})

    tender = relationship("Tender", back_populates="tender_specification")

    def __str__(self):
        return f"Specification for {self.tender.title}"    

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


# Bidder Model
class Bidder(BaseModel):
    __tablename__ = "bidders"
    bidder_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    name = Column(String(255), nullable=False)
    contact_info = Column(Text, nullable=False)
    bid = Column(ARRAY(String))
    additional_attributes = Column(JSON, default={})

    tenant = relationship("Tenant", back_populates="bidders")

    # One-to-one relationship with Bid
    bid = relationship("Bid", back_populates="bidder", uselist=False)

    def __str__(self):
        return self.name


# Bid Model
class Bid(BaseModel):
    __tablename__ = "bids"
    bid_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tender_id = Column(PG_UUID, ForeignKey("tenders.tender_id"), nullable=False)
    bidder_id = Column(PG_UUID, ForeignKey("bidders.bidder_id"), nullable=False, unique=True)  # Foreign key to Bidder
    submission_date = Column(DateTime, nullable=False)
    bid_status_value_id = Column(PG_UUID, nullable=False)
    document = Column(ARRAY(String))
    evaluation_result = Column(ARRAY(String))
    additional_attributes = Column(JSON, default={})

    tender = relationship("Tender", back_populates="bid")
    evaluation_results = relationship("EvaluationResult", back_populates="bid")
    # One-to-one relationship with Bidder
    bidder = relationship("Bidder", back_populates="bid", uselist=False)

    bid_documents = relationship("BidDocument", back_populates="bid", uselist=False)    
    
    # Ensuring unique constraint for the combination of tender_id and bidder_name
    __table_args__ = (
        UniqueConstraint('tender_id', 'bidder_id', name='unique_tender_bidder'),
    )
    
    def __str__(self):
        return f"Bid for {self.tender.title}"

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

    # One-to-many relationship with Bid
    bid = relationship("Bid", back_populates="bid_documents")
    
    def __str__(self):
        return self.file_name

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

    tenant = relationship("Tenant", back_populates="evaluation_method")
    evaluation_criteria = relationship("EvaluationCriteria", back_populates="evaluation_method")
    
    def __str__(self):
        return self.name

# EvaluationCriteria Model
class EvaluationCriteria(BaseModel):
    __tablename__ = "evaluation_criteria"
    criteria_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tender_id = Column(PG_UUID,ForeignKey("tenders.tender_id"), nullable=False, unique=True,)  # Unique constraint for one-to-one
    criteria_details = Column(Text, nullable=False)
    generated_date = Column(DateTime, nullable=False)
    evaluation_method_id = Column(PG_UUID, ForeignKey("evaluation_methods.evaluation_method_id"), nullable=False)
    evaluation_stage = Column(ARRAY(String))
    additional_attributes = Column(JSON, default={})

    tender = relationship("Tender", back_populates="evaluation_criteria")
    evaluation_stages = relationship("EvaluationStage", back_populates="evaluation_criteria")
    evaluation_results = relationship("EvaluationResult", back_populates="evaluation_criteria")
    evaluation_method = relationship("EvaluationMethod", back_populates="evaluation_criteria")

    def __str__(self):
        return f"Evaluation Criteria for {self.tender.title}"


# EvaluationStage Model
class EvaluationStage(BaseModel):
    __tablename__ = "evaluation_stages"
    stage_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tender_id = Column(PG_UUID, ForeignKey("tenders.tender_id"), nullable=False)
    criteria_id = Column(PG_UUID, ForeignKey("evaluation_criteria.criteria_id"), nullable=False)
    stage_type_value_id = Column(PG_UUID, nullable=False)
    sequence = Column(Integer, nullable=False)
    categories = Column(ARRAY(String))

    tender = relationship("Tender", back_populates="evaluation_stages")
    categories = relationship("EvaluationCategory", back_populates="evaluation_stages")
    evaluation_criteria = relationship("EvaluationCriteria", back_populates="evaluation_stages")
    evaluation_results = relationship("EvaluationResult", back_populates="evaluation_stage")

    def __str__(self):
        return f"Evaluation Stage for {self.tender.title}"


# EvaluationCategory Model
class EvaluationCategory(BaseModel):
    __tablename__ = "evaluation_categories"
    category_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    stage_id = Column(PG_UUID, ForeignKey("evaluation_stages.stage_id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    sequence = Column(Integer, nullable=False)
    criteria_list = Column(ARRAY(String))
    additional_attributes = Column(JSON, default={})

    # Relationship to EvaluationStage
    evaluation_stages = relationship("EvaluationStage", back_populates="categories")

    # One-to-many relationship with EvaluationCriterion
    evaluation_criterion = relationship("EvaluationCriterion", back_populates="category")
    evaluation_results = relationship("EvaluationResult", back_populates="evaluation_category")

    def __str__(self):
        return self.name


# EvaluationCriterion Model
class EvaluationCriterion(BaseModel):
    __tablename__ = "evaluation_criterion"
    criterion_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    category_id = Column(PG_UUID, ForeignKey("evaluation_categories.category_id"), nullable=False)
    description = Column(Text, nullable=False)
    weightage = Column(Integer, nullable=False)
    is_mandatory = Column(Boolean, default=True)
    criteria_type_value_id = Column(PG_UUID, nullable=False)
    sequence = Column(Integer, nullable=False)
    additional_attributes = Column(JSON, default={})

    category = relationship("EvaluationCategory", back_populates="evaluation_criterion")
    evaluation_results = relationship("EvaluationResult", back_populates="evaluation_criterion")

    def __str__(self):
        return self.description


# EvaluationResult Model
class EvaluationResult(BaseModel):
    __tablename__ = "evaluation_results"
    result_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    bid_id = Column(PG_UUID, ForeignKey("bids.bid_id"), nullable=False)
    criteria_id = Column(PG_UUID, ForeignKey("evaluation_criteria.criteria_id"), nullable=False)
    stage_id = Column(PG_UUID, ForeignKey("evaluation_stages.stage_id"), nullable=False)
    category_id = Column(PG_UUID, ForeignKey("evaluation_categories.category_id"), nullable=False)
    criterion_id = Column(PG_UUID, ForeignKey("evaluation_criterion.criterion_id"), nullable=False)
    evaluation_outcome_value_id = Column(PG_UUID, nullable=False)
    score = Column(Float, nullable=False)
    comments = Column(Text, nullable=False)
    additional_attributes = Column(JSON, default={})

    bid = relationship("Bid", back_populates="evaluation_results")
    evaluation_criteria = relationship("EvaluationCriteria", back_populates="evaluation_results", lazy="joined" )
    evaluation_stage = relationship("EvaluationStage", back_populates="evaluation_results", lazy="joined")
    evaluation_category = relationship("EvaluationCategory", back_populates="evaluation_results", lazy="joined")
    evaluation_criterion = relationship("EvaluationCriterion", back_populates="evaluation_results", lazy="joined")

    def __str__(self):
        return f"Evaluation Result for {self.bid}"


# ReferenceType Model
class ReferenceType(Base):
    __tablename__ = "reference_types"

    reference_type_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    reference_values = relationship("ReferenceValue", back_populates="reference_type")

    def __str__(self):
        return f"<ReferenceType(name={self.name})>"


# ReferenceValue Model
class ReferenceValue(Base):
    __tablename__ = "reference_values"

    reference_value_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4, nullable=False)
    reference_type_id = Column(PG_UUID, ForeignKey("reference_types.reference_type_id"), nullable=False)
    value = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    sort_order = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    additional_attributes = Column(JSON, default=dict)

    reference_type = relationship("ReferenceType", back_populates="reference_values")

    def __str__(self):
        return f"<ReferenceValue(value={self.value}, code={self.code})>"


# GlobalRole Model
class GlobalRole(BaseModel):
    __tablename__ = "global_roles"
    global_role_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    permission = Column(ARRAY(String))

    global_user_roles = relationship("GlobalUserRole", back_populates="global_role")

    # Many-to-many relationship with Permission
    permissions = relationship("Permission", secondary=global_role_permissions, back_populates="global_roles")
    tenant = relationship("Tenant", back_populates="global_role")

    def __str__(self):
        return self.name


# Integration Model
class Integration(BaseModel):
    __tablename__ = "integrations"
    Integration_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, nullable=False)
    provider_name = Column(String(255), nullable=False)
    integration_type = Column(String(100), nullable=False)
    configuration_details = Column(JSON, default={})
    last_syn_date = Column(DateTime, nullable=False)


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


# Invitation Model
class Invitation(BaseModel):
    __tablename__ = "invitations"

    invitation_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    invited_by_user = Column(PG_UUID, ForeignKey("users.user_id"), nullable=False)
    organization_id = Column(PG_UUID, ForeignKey("organizations.organization_id"), nullable=False)

    invitation_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    invitation_status_value_id = Column(PG_UUID, nullable=False)
    role = Column(ARRAY(String))
    # Relationships
    tenant = relationship("Tenant", back_populates="invitations")
    invited_by = relationship("User", back_populates="invitations")
    organization = relationship("Organization", back_populates="invitations")

    def __str__(self):
        return self.email


# Notification Model
class Notification(BaseModel):
    __tablename__ = "notifications"
    notification_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    recipient_user = Column(PG_UUID, ForeignKey("users.user_id"), nullable=False)
    message = Column(String, nullable=False)
    sent_date = Column(DateTime, nullable=True)
    is_read = Column(Boolean, default=False)
    additional_attributes = Column(JSON, default={})

    # Relationship
    user = relationship("User", back_populates="notifications")
    tenant = relationship("Tenant", back_populates="notifications")

    def __str__(self):
        return f"Notification for {self.actor_user_id}"


# AuditLog Model
class AuditLog(BaseModel):
    __tablename__ = "audit_log"
    log_id = Column(PG_UUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(PG_UUID, ForeignKey("tenants.tenant_id"), nullable=False)
    actor_user_id = Column(PG_UUID, ForeignKey("users.user_id"), unique=True, nullable=False)  # Foreign key to User
    action = Column(String(255), nullable=False)
    action_date = Column(DateTime, nullable=False)
    details = Column(Text, nullable=True)
    additional_attributes = Column(JSON, default=dict)
    # One-to-one relationship with User
    actor_user = relationship("User", back_populates="audit_log", uselist=False)  # One-to-one relationship
    tenant = relationship("Tenant", back_populates="audit_log")

    def __str__(self):
        return f"<AuditLog(action={self.action})>"


Base.metadata.create_all(engine)  # Create tables
