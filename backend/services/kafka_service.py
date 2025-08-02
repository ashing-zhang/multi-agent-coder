from confluent_kafka import Producer, Consumer, KafkaException
from ..core.config import settings
import asyncio
import json

class KafkaService:
    """
    Kafka服务类，用于处理消息的生产和消费。
    """
    def __init__(self):
        # Kafka生产者配置
        producer_conf = {
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS
        }
        self.producer = Producer(producer_conf)
        
        # Kafka消费者配置
        consumer_conf = {
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': 'agent_group',
            'auto.offset.reset': 'earliest'
        }
        self.consumer = Consumer(consumer_conf)
        self.consumer.subscribe([settings.KAFKA_TOPIC_REQUEST])
    
    def produce_message(self, topic: str, message: dict):
        """
        生产消息到指定的Kafka主题。
        :param topic: Kafka主题
        :param message: 消息内容
        """
        try:
            self.producer.produce(topic, json.dumps(message).encode('utf-8'))
            self.producer.flush()
        except KafkaException as e:
            print(f"Kafka生产者错误: {e}")
    
    def consume_messages(self, topic: str, callback):
        """
        从指定的Kafka主题消费消息。
        :param topic: Kafka主题
        :param callback: 处理消息的回调函数
        """
        try:
            self.consumer.subscribe([topic])
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    print(f"Kafka消费者错误: {msg.error()}")
                    continue
                
                # 解析消息
                message = json.loads(msg.value().decode('utf-8'))
                # 调用回调函数处理消息
                callback(message)
        except KafkaException as e:
            print(f"Kafka消费者错误: {e}")
        except KeyboardInterrupt:
            print("Kafka消费者已停止")
        finally:
            self.consumer.close()