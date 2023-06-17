import hydra
from omegaconf import DictConfig

@hydra.main(version_base=None, config_path="configs", config_name="simple_room2")
def my_app(cfg : DictConfig) -> None:
    for room in cfg.rooms:
        print(f"Room: {room.name}")
        for door in room.doors:
            print(f"Door location: {door.location}")
        for obj in room.objects:
            print(f"Object: {obj.name}, Location: {obj.location}")

if __name__ == "__main__":
    my_app()
