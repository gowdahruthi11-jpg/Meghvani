from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.block import Block
from app.models.village import Village

class LocationService:
    @staticmethod
    def get_all_blocks(db: Session, active_only: bool = True) -> List[Block]:
        query = db.query(Block)
        if active_only:
            query = query.filter(Block.active == True)
        return query.all()

    @staticmethod
    def get_block_by_id(db: Session, block_id: int) -> Optional[Block]:
        return db.query(Block).filter(Block.id == block_id).first()

    @staticmethod
    def get_all_villages(db: Session, active_only: bool = True) -> List[Village]:
        query = db.query(Village)
        if active_only:
            query = query.filter(Village.active == True)
        return query.all()

    @staticmethod
    def get_village_by_id(db: Session, village_id: int) -> Optional[Village]:
        return db.query(Village).filter(Village.id == village_id).first()

    @staticmethod
    def get_villages_by_pin(db: Session, pin_code: str) -> List[Village]:
        """
        Retrieves villages linked to a given 6-digit PIN code.
        Farmers enter their PIN code; backend looks up available villages.
        """
        return db.query(Village).filter(
            Village.pin_code == pin_code.strip(),
            Village.active == True
        ).all()

    @staticmethod
    def map_village_to_block(db: Session, village_id: int) -> Optional[Block]:
        """
        Derives the primary forecasting Block automatically from the selected Village.
        Farmers do NOT need to know or guess their administrative block.
        """
        village = db.query(Village).filter(Village.id == village_id).first()
        if not village:
            return None
        return db.query(Block).filter(Block.id == village.block_id).first()
