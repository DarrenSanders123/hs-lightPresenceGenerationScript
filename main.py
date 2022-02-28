import sys
import random


# noinspection PyMethodMayBeStatic
class AutomationScript:

    def __init__(self):
        self.input_boolean_id = str()
        self.id = str()
        self.automationName = str()
        self.name = str()

        self.light_group = list()
        self.light_group_id = str()

        self.door_sensor_group = list()
        self.door_sensor_group_id = str()

        self.motion_sensor_group = list()
        self.motion_sensor_group_id = str()

        self.automationFileContent = str()
        self.configFileContent = str()

        print("\n"
              "-------------------------------\n"
              "Copyright Darren Sanders ~ 2022\n"
              "-------------------------------\n"
              "\n"
              "This script will generate a automation yaml file,\n"
              "as well as a configuration.yaml file. (for the custom input_booleans)")

        options = sys.argv
        if '--help' in options:
            self.help()
        elif '--no-gui' in options:
            self.commandline_interface()
        elif '--gui' in options:
            self.gui_interface()
        elif options[1] is None:
            self.help()

    def generate_automation_name(self):
        self.id = str(int(random.Random().random() * 999999) + 1)

        self.automationName = self.id + '_' + self.name + "_automatic_lights"

    def ask_name(self):
        self.name = input("\nEnter room name:\n")

    def help(self):
        print('help:\n'
              '     --help      Opens this screen.\n'
              '     --no-gui    Runs it using the commandline interface.\n'
              '     --gui       !!NOT IMPLEMENTED!! Runs the custom gui (might be buggy).\n')

    def generate_light_group(self):
        self.configFileContent += "\nlight:" \
                                  "\n   - platform: group" \
                                  "\n     name: " + self.id + "_" + self.name + "_light_group" \
                                                                "\n     entities:"
        for entity in self.light_group:
            self.configFileContent += "\n       - " + entity

        self.light_group_id = "light." + self.id + "_" + self.name + "_light_group"

    def generate_door_sensor_group(self):
        self.configFileContent += "\nbinary_sensor:" \
                                  "\n   - platform: group" \
                                  "\n     name: " + self.id + "_" + self.name + "_door_sensor_group" \
                                                                "\n     device_class: door" \
                                                                "\n     entities:"
        for entity in self.door_sensor_group:
            self.configFileContent += "\n       - " + entity

        self.door_sensor_group_id = "binary_sensor." + self.id + "_" + self.name + "_door_sensor_group"

    def generate_motion_sensor_group(self):
        self.configFileContent += "\nbinary_sensor:" \
                                  "\n   - platform: group" \
                                  "\n     name: " + self.id + "_" + self.name + "_motion_sensor_group" \
                                                                "\n     device_class: motion" \
                                                                "\n     entities:"
        for entity in self.motion_sensor_group:
            self.configFileContent += "\n       - " + entity

        self.motion_sensor_group_id = "binary_sensor." + self.id + "_" + self.name + "_motion_sensor_group"

    def generate_input_booleans(self):
        self.input_boolean_id = "presence_" + self.id + "_" + self.name

        self.configFileContent += "\ninput_boolean:" \
                                  "\n     " + self.input_boolean_id + ":" + \
                                  "\n       name: Presence" + self.name.capitalize()

    def commandline_interface(self):
        self.ask_name()
        self.generate_automation_name()

        name = self.name

        if '--no-gui' in sys.argv:
            print("Enter the door sensors (accepted types: binary_sensor)")
            entities = input("Enter entity ID's and separate them with a ',':\n").replace(" ", '')
            entities = list(entities.split(','))

            print("Enter the motion sensors (accepted types: binary_sensor")
            motion_entities = input("Enter the entity ID's and separate them with a ','\n").replace(" ", "")
            motion_entities = list(motion_entities.split(","))

            print("Enter the entities to control with this automation (accepted types: light)")
            entities_to_control = input("Enter the entity ID's and separate them with a ',':\n").replace(" ", "")
            entities_to_control = list(entities_to_control.split(","))

            self.automationFileContent += "alias: " + self.automationName
            self.automationFileContent += "\ndescription: 'automatically turn on and off lights based on motion'"

            for entity in entities:
                self.automationFileContent += "\ntrigger:\n" \
                                              "  - platform: state\n" \
                                              "    entity_id: " + entity + "\n" \
                                                                             "    to: 'on'"

            self.automationFileContent += "\ncondition: []" \
                                          "\naction:" \
                                          "\n  - choose:" \
                                          "\n      - conditions:"

            self.light_group = entities_to_control
            self.generate_light_group()

            self.door_sensor_group = entities
            self.generate_door_sensor_group()

            self.motion_sensor_group = motion_entities
            self.generate_motion_sensor_group()

            self.generate_input_booleans()

            self.automationFileContent += "\n          - condition: state" \
                                          "\n            entity_id: " + self.light_group_id + \
                                          "\n            state: 'on'"

            self.automationFileContent += "\n        sequence:" \
                                          "\n          - wait_for_trigger:" \
                                          "\n              - platform: state" \
                                          "\n                entity_id: " + self.door_sensor_group_id + \
                                          "\n                from: 'on'" \
                                          "\n                to: 'off'" \
                                          "\n            continue_on_timeout: false"

            self.automationFileContent += "\n    default:" \
                                          "\n      - service: light.turn_on" \
                                          "\n        data: {}" \
                                          "\n        target:" \
                                          "\n           entity_id: " + self.light_group_id

            self.automationFileContent += "\n      - wait_for_trigger:" \
                                          "\n          - platform: state" \
                                          "\n            entity_id: " + self.door_sensor_group_id + \
                                          "\n            from: 'on'" \
                                          "\n            to: 'off'" \
                                          "\n        continue_on_timeout: false"

            self.automationFileContent += "\n  - wait_template: '{{is_state(''" + self.motion_sensor_group_id + "'', ''on'')}}'" \
                                          "\n    timeout: 20" \
                                          "\n    continue_on_timeout: true"

            self.automationFileContent += "\n  - choose:" \
                                          "\n      - conditions:" \
                                          "\n          - condition: template" \
                                          "\n            value_template: '{{ not wait.completed }}'" \
                                          "\n        sequence:" \
                                          "\n          - service: input_boolean.turn_off" \
                                          "\n            data: {}" \
                                          "\n            target:" \
                                          "\n              entity_id: input_boolean." + self.input_boolean_id + \
                                          "\n    default:" \
                                          "\n        - service: input_boolean.turn_on" \
                                          "\n          data: {}" \
                                          "\n          target:" \
                                          "\n            entity_id: input_boolean." + self.input_boolean_id

            self.automationFileContent += "\n  - wait_template: '{{is_state(input_boolean." + self.input_boolean_id + ", off) }}'" + \
                                          "\n  - service: light.turn_off" \
                                          "\n    data: {}" \
                                          "\n    target:" \
                                          "\n       entity_id: " + self.light_group_id
            self.automationFileContent += "\nmode: parallel" \
                                          "\nmax: 10"

            print(self.automationFileContent)
            print(self.configFileContent)

    def gui_interface(self):
        self.help()
        return NotImplementedError("this has not been developed yet")


AutomationScript()
