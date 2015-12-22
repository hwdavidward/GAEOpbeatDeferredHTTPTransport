# GAEOpbeatDeferredHTTPTransport
Google App Engine Opbeat Deferred HTTPTransport Class

This provides a way to perform async requests with GAE and Opbeat. The built in ASYNC from Opbeat will not work because threads can not live past a given request. As such the GAEDeferredHTTPTransport class defers this work with the use of hte built in deferred library.

##Set-Up:
When you configure opbeat simply override the opbeat.client._transport_class with the GAEDeferredHTTPTransport class. With this done your requests to opbeat will be use the deferred library and will be placed on a GAE Task Queue to be processed later. 

######Flask Example:
    ```
    opbeat = Opbeat(main_app)
    from app.gae_deferred_transport import GAEDeferredHTTPTransport
    opbeat.client._transport_class = GAEDeferredHTTPTransport
    ```

##Specific Task Queue:
If you wish to use a specific queue then pass _queue='opbeat-activity-tracking' or whatever queue name you have added in your deferred.defer method call.

######Example:
    ```
	deferred.defer(self.send_request, _queue='opbeat-activity-tracking', **kwargs)
    ```