import hydra
from omegaconf import DictConfig

@hydra.main(version_base=None, config_path="configs", config_name="simple_room")
def my_app(cfg : DictConfig) -> None:
    for room in cfg.rooms:
        print(f"Room: {room.name}")
        for obj in room.objects:
            print(f"Object: {obj.name}")
        for key in room.doorkeys:
            print(f"Key for room: {key.forroom}")

if __name__ == "__main__":
    my_app()
