import AlteryxPythonSDK as Sdk
import xml.etree.ElementTree as Et
import time
import paho.mqtt.client as mqtt

class AyxPlugin:
    def __init__(self, n_tool_id: int, alteryx_engine: object, output_anchor_mgr: object):
        # Default properties
        self.n_tool_id: int = n_tool_id
        self.alteryx_engine: Sdk.AlteryxEngine = alteryx_engine
        self.output_anchor_mgr: Sdk.OutputAnchorManager = output_anchor_mgr

        self.server = None
        self.topic = None
        self.capture_seconds = None

        self.is_initialized = True

        pass

    def pi_init(self, str_xml: str):
        self.output_anchor = self.output_anchor_mgr.get_output_anchor('Output')
        self.server = Et.fromstring(str_xml).find('Server').text if 'Server' in str_xml else None
        self.topic = Et.fromstring(str_xml).find('Topic').text  if 'Topic' in str_xml else None
        self.capture_seconds = int(Et.fromstring(str_xml).find('Seconds').text)  if 'Seconds' in str_xml else None

        if self.server is None:
            self.display_error_msg("Enter a valid server name")

        if self.topic is None:
            self.display_error_msg("Enter a valid topic to subscribe to")
        pass

    def pi_add_incoming_connection(self, str_type: str, str_name: str) -> object:
        return self

    def pi_add_outgoing_connection(self, str_name: str) -> bool:
        return True


    def get_messages(self):

        messages = []
        connection_codes = {0 : 'Connection accepted',
                            1 : 'Connection refused, unacceptable protocol version',
                            2 : 'Connection refused, identifier rejected',
                            3 : 'Connection refused, server unavailable',
                            4 : 'Connection refused, bad user name or password',
                            5 : 'Connection refused, not authorized'}

        # The callback for when the client receives a CONNACK response from the server.
        def on_connect(client, userdata, flags, rc):
            self.display_info(f'Connected with result code {str(rc)} : {connection_codes[rc]}')

            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe(self.topic)

        # The callback for when a PUBLISH message is received from the server.
        def on_message(client, userdata, msg):
            messages.append(str(msg.payload.decode("UTF-8")).strip())

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        try:
            client.connect(self.server, 1883, 60)
            client.loop_start()
            self.display_info(f'Capturing data for {self.capture_seconds} seconds')
            time.sleep(self.capture_seconds) # wait
            client.loop_stop() #stop the loop
        except ConnectionRefusedError as ex:
            self.display_error_msg(f'Unable to connect to {self.server}')

        return messages
      

    def build_record_info_out(self):
        """
        A non-interface helper for pi_push_all_records() responsible for creating the outgoing record layout.
        :param file_reader: The name for csv file reader.
        :return: The outgoing record layout, otherwise nothing.
        """

        record_info_out = Sdk.RecordInfo(self.alteryx_engine)  # A fresh record info object for outgoing records.
        #We are returning a single column and a single row. 
        record_info_out.add_field('Topic', Sdk.FieldType.string, 1000, source='MQTT Subscribe', description='Topic')
        record_info_out.add_field('Message', Sdk.FieldType.string, 1000, source='MQTT Subscribe', description='Message')

        return record_info_out

    def pi_push_all_records(self, n_record_limit: int) -> bool:

        if not self.is_initialized:
            return False

        record_info_out = self.build_record_info_out()  # Building out the outgoing record layout.
        self.output_anchor.init(record_info_out)  # Lets the downstream tools know of the outgoing record metadata.
        record_creator = record_info_out.construct_record_creator()  # Creating a new record_creator for the new data.

        if self.alteryx_engine.get_init_var(self.n_tool_id, 'UpdateOnly') == 'True':
            return False

        output_data = self.get_messages()

        for msg in output_data:
            record_info_out[0].set_from_string(record_creator, self.topic)
            record_info_out[1].set_from_string(record_creator, msg)

            out_record = record_creator.finalize_record()
            self.output_anchor.push_record(out_record, False)  # False: completed connections will automatically close.
            record_creator.reset()  # Resets the variable length data to 0 bytes (default) to prevent unexpected results.


        self.display_info(f'Captured {len(output_data)} messages')
        self.output_anchor.close()  # Close outgoing connections.
        return True

    def pi_close(self, b_has_errors: bool):
        self.output_anchor.assert_close()  # Checks whether connections were properly closed.

    def display_error_msg(self, msg_string: str):
        self.alteryx_engine.output_message(self.n_tool_id, Sdk.EngineMessageType.error, msg_string)
        self.is_initialized = False

    def display_info(self, msg_string: str):
        self.alteryx_engine.output_message(self.n_tool_id, Sdk.EngineMessageType.info, msg_string)


class IncomingInterface:
    def __init__(self, parent: AyxPlugin):
        pass

    def ii_init(self, record_info_in: Sdk.RecordInfo) -> bool:
        pass

   
    def ii_push_record(self, in_record: Sdk.RecordRef) -> bool:
        pass

    def ii_update_progress(self, d_percent: float):
        # Inform the Alteryx engine of the tool's progress.
        pass


    def ii_close(self):
        pass
