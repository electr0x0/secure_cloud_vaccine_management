from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.network import VPC, InternetGateway, NATGateway, RouteTable
from diagrams.aws.security import SecurityHub as SecurityGroup
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
from diagrams.aws.general import Users
from diagrams.onprem.compute import Server
from diagrams.onprem.database import MySQL
from diagrams.generic.network import VPN
from diagrams.programming.framework import React
from diagrams.programming.language import Python

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
        "fontname": "Arial",
    }

    node_attr = {
        "fontsize": "12",
        "fontname": "Arial",
        "margin": "0.4",
    }

    edge_attr = {
        "fontsize": "10",
        "fontname": "Arial",
        "labeldistance": "2.0",
        "labelangle": "-45",
    }

    with Diagram(
        "Cloud Vaccine System Architecture (Hybrid)",
        show=True,
        direction="LR",
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
        filename="aws_hybrid_architecture"
    ):
        users = Users("End Users")
        
        with Cluster("AWS Cloud"):
            igw = InternetGateway("Internet\nGateway")

            with Cluster("VPC (10.0.0.0/16)"):
                with Cluster("Public Subnet (10.0.1.0/24)"):
                    with Cluster("Public Security Groups"):
                        frontend_sg = SecurityGroup("Frontend SG\n(80, 443)")
                        backend_sg = SecurityGroup("Backend SG\n(8000)")

                    frontend = EC2("Frontend\nNextJS\n(t2.micro)")
                    backend = EC2("Backend\nFastAPI\n(t2.micro)")

                with Cluster("Private Subnet (10.0.2.0/24)"):
                    with Cluster("Private Security Groups"):
                        db_sg = SecurityGroup("MariaDB SG\n(3306)")

                    db = RDS("Cloud DB\nMariaDB\n(t2.micro)")

        with Cluster("On-Premises Infrastructure"):
            with Cluster("Private Network (Secure Zone)"):
                tailscale = VPN("Tailscale\nWireGuard VPN")
                
                with Cluster("Key Management Services"):
                    keyserver = Server("Key Server\nFastAPI\n(t3.small)")
                    keydb = MySQL("Key Database\nMariaDB")
                    
                    
                    keyserver >> Edge(color="red", style="dotted", label="3306") >> keydb

        
        users >> Edge(color="blue", style="bold", label="HTTPS") >> igw
        igw >> Edge(label="80/443", color="blue") >> frontend_sg >> frontend
        frontend >> Edge(label="8000", color="darkgreen") >> backend_sg >> backend
        
        
        backend >> Edge(label="3306", color="red", minlen="1") >> db_sg >> db
        
        
        backend >> Edge(
            label="8081",
            color="purple",
            style="dashed",
            minlen="1",
            ltail="cluster_0",
            labeldistance="4.5",
            labelangle="0"
        ) >> tailscale >> keyserver

if __name__ == "__main__":
    create_aws_diagram()