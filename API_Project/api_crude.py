# API Crude
# Author: Mauricio Neves Junior
# Version: 1.0
# Date: 07/12/2023

# Libraries
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# FastAPI Models
class Device(BaseModel):
    device_id: str
    protocol: str
    address: str
    topic: str = None

# Existent Database Model
Base = declarative_base()

class ExistingDevice(Base):
    __tablename__ = 'existing_devices'
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True)
    temperature = Column(Integer)

# Model For Second Database
class NewDevice(Base):
    __tablename__ = 'new_devices'
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True)
    protocol = Column(String)
    address = Column(String)
    topic = Column(String)


def main():
    # Database Connection
    existing_engine = create_engine("sqlite:///./database.db")
    new_engine = create_engine("sqlite:///./devices.db")

    Base.metadata.create_all(bind=existing_engine)
    Base.metadata.create_all(bind=new_engine)

    # Creating sessions for databases
    ExistingSession = sessionmaker(autocommit=False, autoflush=False, bind=existing_engine)
    NewSession = sessionmaker(autocommit=False, autoflush=False, bind=new_engine)

    app = FastAPI()

    # Route for reading the existent database data
    @app.get("/existing_devices/{device_id}")
    def read_existing_device(device_id: str):
        session = ExistingSession()
        db_device = session.query(ExistingDevice).filter(ExistingDevice.device_id == device_id).first()
        session.close()
        if db_device is None:
            raise HTTPException(status_code=404, detail="Device not found")
        return db_device

    # Route for create and add data in the new database
    @app.post("/new_devices/")
    def create_new_device(device: Device):
        session = NewSession()
        db_device = NewDevice(**device.dict())
        session.add(db_device)
        session.commit()
        session.refresh(db_device)
        session.close()
        return db_device
