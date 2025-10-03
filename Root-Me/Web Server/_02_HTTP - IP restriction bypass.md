# HTTP - IP restriction bypass

This took me some time as I wasn't familiar with HTTP headers and BurpSuite. Basically, the challenge requires the user to find the flag without logging in. The challenge 
explicitly tells the user that credentials aren't required as long as the user is on the same LAN network as the host. 

## Step 1: Copy the website URL and open it in the BurpSuite Browser. Add the website to scope and input random credentials with the intercept on. <br>
<img width="698" height="250" alt="image" src="https://github.com/user-attachments/assets/84ba7087-eef9-40bc-9347-3d48167658d3" />
<br>
<img width="1138" height="502" alt="image" src="https://github.com/user-attachments/assets/f9ac279e-ae82-4de9-94a5-a1896ac79f8e" />
<br>

## Step 2: Send this request to the repeater. Now add the `X-Forwarded-For` header with the value `192.168.0.1` which is the default gateway. This would trick the server 
into thinking the user is connected to the same LAN server. <br>
<img width="990" height="445" alt="image" src="https://github.com/user-attachments/assets/088af04a-1d3b-4777-aa60-9059a62d050d" />

<br>

## Step 3: Hit "Send" on the repeater. You'll get the password.
<br>
<img width="1016" height="784" alt="image" src="https://github.com/user-attachments/assets/74ad437c-113a-441d-afcc-d903fed01848" />
<br>
The password is: `Ip_$po0Fing`



The `X-Forwarded-For` header is used in HTTP requests to keep track of the original IP address of the client when the request passes through proxies.
<br>
While it is used by servers to identify who is sending the request, it can also easily be used to spoof IP addresses.
