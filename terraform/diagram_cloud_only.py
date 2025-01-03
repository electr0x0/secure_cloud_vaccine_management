from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.network import VPC, InternetGateway, NATGateway, RouteTable
from diagrams.aws.security import SecurityHub as SecurityGroup
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
from diagrams.aws.general import Users

def create_aws_diagram():
    graph_attr = {
        "fontsize": "20",
        "bgcolor": "white",
        "splines": "ortho",
        "pad": "1.5",
        "nodesep": "0.8",
        "ranksep": "1.0",
        "marginx": "2.0",
        "marginy": "2.0",
    }

    node_attr = {
        "fontsize": "12",
        "fontname": "Arial",
        "margin": "0.4",
    }

    edge_attr = {
        "fontsize": "10",
        "fontname": "Arial",
    }

    with Diagram(
        "Cloud Vaccine System Architecture",
        show=True,
        direction="LR",
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
        filename="aws_architecture"
    ):
        users = Users("End Users")
        
        with Cluster("AWS Cloud"):
            igw = InternetGateway("Internet\nGateway")

            with Cluster("VPC (10.0.0.0/16)"):
                with Cluster("Public Subnet (10.0.1.0/24)"):
                    with Cluster("Public Security Groups"):
                        frontend_sg = SecurityGroup("Frontend SG")
                        backend_sg = SecurityGroup("Backend SG")

                    frontend = EC2("Frontend\n(t2.micro)")
                    backend = EC2("Backend\n(t2.micro)")

                with Cluster("Private Subnet (10.0.2.0/24)"):
                    with Cluster("Private Security Groups"):
                        db_sg = SecurityGroup("MariaDB SG")
                        keyserver_sg = SecurityGroup("Key Server SG")

                    db = EC2("MariaDB\n(t2.micro)")
                    keyserver = EC2("Key Server\n(t3.small)")

        # Define connections with better edge styling
        users >> Edge(color="blue", style="bold") >> igw
        igw >> Edge(label="80/443", color="blue") >> frontend_sg >> frontend
        frontend >> Edge(label="8000", color="darkgreen") >> backend_sg >> backend
        
        # Connections to private subnet
        backend >> Edge(label="3306", color="red", minlen="1") >> db_sg >> db
        backend >> Edge(label="8081", color="purple", minlen="1") >> keyserver_sg >> keyserver

if __name__ == "__main__":
    create_aws_diagram() 