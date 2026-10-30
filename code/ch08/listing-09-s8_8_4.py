# Extracted from manuscript/book1-traditional/08-web-application-fundamentals.md §8.8.4 (listing 9). Edit the manuscript, not this file.
# pip install grpcio grpcio-tools
# python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. orders.proto
import grpc
import orders_pb2
import orders_pb2_grpc

with grpc.insecure_channel("localhost:50051") as channel:   # use TLS credentials in production
    stub = orders_pb2_grpc.OrderServiceStub(channel)

    # Unary call with a 200 ms deadline.
    try:
        order = stub.GetOrder(orders_pb2.GetOrderRequest(order_id="o-42"), timeout=0.2)
        print(order.order_id, orders_pb2.OrderStatus.Name(order.status))
    except grpc.RpcError as err:
        if err.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            print("gave up after 200 ms; serve a fallback")
        else:
            raise

    # Server streaming: iterate over responses as they arrive.
    for event in stub.WatchOrderStatus(orders_pb2.GetOrderRequest(order_id="o-42"),
                                       timeout=30):
        print(orders_pb2.OrderStatus.Name(event.status))
