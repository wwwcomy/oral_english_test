
kubectl cp my-pod:/path/to/file ./localfile
nano localfile  
kubectl cp ./localfile my-pod:/path/to/file

kc exec -it tmp-pod -nshim -- bash 

kubectl run tmp-pod --image=ubuntu -nshim --restart=Never -nshim -- sleep 360000