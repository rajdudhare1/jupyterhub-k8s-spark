# To enable spark to work with your cluster run below commands
# First create service account that will be used to submit your jobs to k8s cluster
# To create a custom service account, a user can use the kubectl create serviceaccount command. For example, the following command creates a service account named spark:
# Assuming you are using default namespace for spark

kubectl create serviceaccount spark

# To grant a service account a Role or ClusterRole, a RoleBinding or ClusterRoleBinding is needed. To create a RoleBinding or ClusterRoleBinding, a user can use the kubectl create rolebinding (or clusterrolebinding for ClusterRoleBinding) command. For example, the following command creates an edit ClusterRole in the default namespace and grants it to the spark service account created above:

kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default


# Create configmap of spark-defaults.conf
kubectl create cm spark-config-jupyter --from-file=spark-defaults.conf
