import configparser







if __name__ == "__main__":
    masks = read_masks_for_name_from_config_file("./config/config.ini", "images")
    print("masks: {}".format(masks))
