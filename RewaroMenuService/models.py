from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, Table, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
import os

Base = declarative_base()

# Association tables for many-to-many relationships
item_variation = Table(
    'item_variation',
    Base.metadata,
    Column('item_id', Integer, ForeignKey('menu_items.id'), primary_key=True),
    Column('variation_id', Integer, ForeignKey('variations.id'), primary_key=True)
)

item_addon = Table(
    'item_addon',
    Base.metadata,
    Column('item_id', Integer, ForeignKey('menu_items.id'), primary_key=True),
    Column('addon_id', Integer, ForeignKey('addons.id'), primary_key=True)
)

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    outlet_id = Column(Integer, nullable=False, index=True)  # Foreign key to merchant_master_data
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    items = relationship('MenuItem', back_populates='category')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'outlet_id': self.outlet_id,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MenuItem(Base):
    __tablename__ = 'menu_items'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String(255), nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    outlet_id = Column(Integer, nullable=False, index=True)  # Foreign key to merchant_master_data
    is_vegetarian = Column(Boolean, default=False)
    is_spicy = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    category = relationship('Category', back_populates='items')
    variations = relationship('Variation', secondary=item_variation, back_populates='items')
    addons = relationship('Addon', secondary=item_addon, back_populates='items')
    
    def to_dict(self, include_relations=True):
        item_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'category_id': self.category_id,
            'outlet_id': self.outlet_id,
            'is_vegetarian': self.is_vegetarian,
            'is_spicy': self.is_spicy,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            item_dict['variations'] = [v.to_dict(include_relations=False) for v in self.variations]
            item_dict['addons'] = [a.to_dict(include_relations=False) for a in self.addons]
        
        return item_dict

class Variation(Base):
    __tablename__ = 'variations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price_adjustment = Column(Float, default=0.0)  # Price modifier for this variation
    outlet_id = Column(Integer, nullable=False, index=True)  # Foreign key to merchant_master_data
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    items = relationship('MenuItem', secondary=item_variation, back_populates='variations')
    
    def to_dict(self, include_relations=True):
        var_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price_adjustment': self.price_adjustment,
            'outlet_id': self.outlet_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations and hasattr(self, 'items'):
            var_dict['items'] = [i.id for i in self.items]
        
        return var_dict

class Addon(Base):
    __tablename__ = 'addons'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    outlet_id = Column(Integer, nullable=False, index=True)  # Foreign key to merchant_master_data
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    items = relationship('MenuItem', secondary=item_addon, back_populates='addons')
    
    def to_dict(self, include_relations=True):
        addon_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'outlet_id': self.outlet_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations and hasattr(self, 'items'):
            addon_dict['items'] = [i.id for i in self.items]
        
        return addon_dict

def get_db_url():
    """Get database URL from environment variables"""
    username = os.environ.get('DB_USERNAME')
    password = os.environ.get('DB_PASSWORD')
    host = os.environ.get('DB_HOST')
    port = os.environ.get('DB_PORT', '5432')
    database = os.environ.get('DB_NAME')
    
    return f'postgresql://{username}:{password}@{host}:{port}/{database}'

def init_db():
    """Initialize database connection without creating tables"""
    engine = create_engine(get_db_url())
    # No longer creating tables automatically
    # Base.metadata.create_all(engine)
    return engine
