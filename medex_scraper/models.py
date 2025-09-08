"""
Database models for medicine data using SQLAlchemy
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import os

Base = declarative_base()

class Medicine(Base):
    __tablename__ = 'medicines'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic Information
    brand_id = Column(String(50), unique=True, index=True)  # External brand ID from medex
    name = Column(String(500), nullable=False, index=True)  # Increased for longer medicine names
    generic_name = Column(String(500), index=True)  # Increased for complex generic names
    strength = Column(String(200))  # Increased for complex dosage strengths
    dosage_form = Column(String(200))  # Increased for detailed dosage forms
    manufacturer = Column(String(500), index=True)  # Increased for long manufacturer names
    
    # Pricing Information
    unit_price = Column(Float)
    pack_price = Column(Float)
    strip_price = Column(Float)
    pack_info = Column(Text)  # Changed to Text for unlimited length
    
    # Medical Information
    indications = Column(Text)
    composition = Column(Text)
    mode_of_action = Column(Text)
    dosage = Column(Text)
    side_effects = Column(Text)
    contraindications = Column(Text)
    precautions = Column(Text)
    interaction = Column(Text)
    overdose_effects = Column(Text)
    pregnancy_category = Column(Text)  # Changed to Text for unlimited length
    storage_conditions = Column(Text)
    drug_classes = Column(Text)  # Changed to Text for unlimited length
    
    # URLs and Meta
    url = Column(Text)  # Changed to Text for very long URLs
    pack_image_url = Column(Text)  # Changed to Text for very long image URLs
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Indexes for better query performance
    __table_args__ = (
        Index('idx_medicine_search', 'name', 'generic_name'),
        Index('idx_medicine_manufacturer', 'manufacturer'),
        Index('idx_medicine_scraped', 'scraped_at'),
    )
    
    def __repr__(self):
        return f"<Medicine(name='{self.name}', manufacturer='{self.manufacturer}')>"

class DatabaseManager:
    """Database manager for handling connections and operations"""
    
    def __init__(self, connection_string=None):
        if connection_string is None:
            # Default connection for localhost:5433
            connection_string = "postgresql://postgres:postgres@localhost:5433/medex_db"
        
        self.engine = create_engine(connection_string, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
        print("✅ Database tables created successfully")
    
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
    
    def test_connection(self):
        """Test database connection"""
        try:
            from sqlalchemy import text
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

# Default database manager instance
db_manager = DatabaseManager()
