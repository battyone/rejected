Changelog
=========

4.0.0 (Unreleased)
------------------

Breaking Changes
^^^^^^^^^^^^^^^^
- REMOVED ``rejected.consumer.Consumer.reply`` as it was wonky and problematic
- REMOVED ``rejected.consumer.Consumer.statsd_*`` functions that were deprecated in v3.13.0
- REMOVED ``rejected.consumer.PublishingConsumer`` class that was deprecated in v3.17.0
- REMOVED ``rejected.consumer.SmartPublishingConsumer`` class that was deprecated in v3.17.0
- CHANGED when a message is returned from RabbitMQ so that it will no longer invoke :meth:`rejected.consumer.Consumer.process`
- CHANGED :meth:`rejected.consumer.Consumer.on_finish` to pass in the instance of an exception if one is raised during the processing of a message. (`#24 <https://github.com/gmr/rejected/issues/24>`_, `#27 <https://github.com/gmr/rejected/issues/27>`_)
- MOVED ``rejected.consumer.SmartConsumer`` to :class:`rejected.smart_consumer.SmartConsumer`
- RENAMED ``rejected.mixins.GarbargeCollectorMixin`` to :class:`rejected.mixins.GarbageCollector`
- REMOVED the ``channel`` argument from :meth:`rejected.consumer.Consumer.publish_message`
- REMOVED imports of :class:`rejected.consumer.Consumer`, :class:`rejected.smart_consumer.SmartConsumer` and the exceptions into the top-level `rejected` namespace.

High-Level Changes
^^^^^^^^^^^^^^^^^^
- Refactored publishing with publisher confirmations enabled to return a :class:`tornado.concurrent.Future` that can be yielded on to wait for confirmations to be returned
- When publisher confirmations are enabled, all publishing is done with the ``mandatory`` flag set
- Documentation cleaned up and rewritten in parts

Other Changes
^^^^^^^^^^^^^
- ADDED :attr:`rejected.consumer.Consumer.rpc_reply` as a replacement of ``rejected.consumer.Consumer.reply``
- ADDED ability to :class:`rejected.data.Properties` to allow for keyword arguments
- ADDED :const:`rejected.consumer.Consumer.IGNORE_OOB_STATS` to not log when ``rejected.consumer.Consumer.stats_*`` calls are made when no message is currently being processed
- ADDED :class:`rejected.log.CorrelationID`` and :class:`rejected.log.NoCorrelationID` as a replacement of :class:`rejected.log.CorrelationFilter`
- ADDED When a :exc:`rejected.errors.ConfigurationException` is raised in :meth:`~rejected.consumer.Consumer.prepare` or :meth:`~rejected.consumer.Consumer.process` it's not longer treated as an unhandled exception and will cause the consumer to shutdown
- ADDED When a :exc:`rejected.errors.ConfigurationException` is raised when initializing a consumer, it will now explicitly shutdown the consumer process
- REMOVED code duplication when dealing with :class:`rejected.consumer.Consumer` property methods
- ADDED additional exception handling support in :class:`rejected.testing.AsyncTestCase`
- REMOVED catching of KeyboardInterrupt in :meth:`rejected.consumer.Consumer.execute` favoring catching higher up in the processing flow
- ADDED call to :meth:`rejected.consumer.Consumer.shutdown` in :meth:`rejected.testing.AsyncTestCase.tearDown` (#25 `nvllsvm <https://github.com/nvllsvm>`_)
- CHANGED :class:`rejected.smart_consumer.SmartConsumer` to load libraries for serialization and compression on demand, reducing the overall memory footprint
- CHANGED :class:`rejected.smart_consumer.SmartConsumer` parsing of ``content-type`` to use `ietfparse <https://pypi.python.org/pypi/ietfparse>`_, including charset for use in decoding in Python 3
- CHANGED In :class:`rejected.smart_consumer.SmartConsumer` attempting to auto-encode or auto-serialize a non-string or non-bytes object with an invalid content encoding or content type will now raise a :exc:`ValueError`
- CHANGED :class:`rejected.smart_consumer.SmartConsumer` auto-serialization of CSV to use :class:`csv.DictWriter` and it now expects a list of dict rows
- ADDED the raising of a `rejected.errors.MessageException` in :class:`rejected.smart_consumer.SmartConsumer` when attempting to decode a message body and a decoding error is raised
- CHANGED :class:`rejected.smart_consumer.SmartConsumer` auto-serialization to JSON to no longer ensure ``ASCII=True``
- ADDED type-hinting to bs4 parsing based upon the ``content-type`` in :class:`rejected.smart_consumer.SmartConsumer`
- MOVED all exceptions to ``rejected.errors``
- ADDED ability to disable including the hostname when submitting stats to statsd

Bug Fixes
^^^^^^^^^
- REMOVED extra call to :meth:`rejected.consumer.Consumer.initialize` in :meth:`rejected.testing.AsyncTestCase._create_consumer` `#21 <https://github.com/gmr/rejected/pull/21>`_ - `dave-shawley <https://github.com/dave-shawley>`_
- CHANGED :attr:`rejected.consumer.Consumer.io_loop` to correctly return the proper loop

3.19.5
------

- Add SSL connection flag support to configuration `#20 <https://github.com/gmr/rejected/pull/20>`_ - `code-fabriek <https://github.com/code-fabriek>`_
- Fix documentation for ``rejected.data.Measurement``
- Alter logging levels for connection failures
- Add ``rejected.testing.AsyncTestCase.measurement``

3.19.4
------

- Try to handle a MCP process cleanup race condition better (Sentry REJECTED-DA)

3.19.3
------

- Really fix a bug with the processing time and message age metrics

3.19.2
------

- Fix a bug with the processing time and message age metrics
- Catch a timeout when waiting on a zombie

3.19.1
------

- Fix a bug in the new durations code

3.19.0
------

- Sentry client changes:
  - Do not assign version, let the client figure that out
  - Do not specify the versions of loaded modules, let the client figure that out
- Add ``rejected.data.Measurement.add_duration``, changing the behavior of
  recorded durations, creating a stack of timings instead of a single timing
  for the key. For InfluxDB submissions, if there is a only a single value,
  that metric will continue to submit as previous versions. If there are multiple,
  the average, min, max, median, and 95th percentile values will be submitted.
- Add ``rejected.consumer.Consumer.stats_add_duration``
- Deprecate ``rejected.consumer.Consumer.stats_add_timing``
- Deprecate ``rejected.consumer.Consumer.stats_add_timing``
- Consumer tags are now in the format ``[consumer-name]-[os PID]``
- Created a base exception class ``rejected.consumer.RejectedException``
- ``rejected.consumer.ConsumerException``, ``rejected.consumer.MessageException``,
  and ``rejected.consumer.ProcessingException`` extend ``rejected.consumer.RejectedException``
- If a ``rejected.consumer.ConsumerException``, ``rejected.consumer.MessageException``,
  or ``rejected.consumer.ProcessingException`` are passed a keyword of ``metric``,
  the consumer will automatically instrument a counter (statsd) or tag (InfluxDB)
  using the ``metric`` value.
- ``rejected.consumer.ConsumerException``, ``rejected.consumer.MessageException``,
  and ``rejected.consumer.ProcessingException`` now support "new style" string formatting,
  automatically applying the args and keyword args that are passed into the creation
  of the exception.
- Logging levels for exceptions changed:
  - ``rejected.consumer.ConsumerException`` are logged with error
  - ```rejected.consumer.MessageException`` are logged with info
  - ```rejected.consumer.ProcessingException`` are logged with warning
- Fix the handling of child startup failures in the MCP
- Fix a bug where un-configured consumers caused an exception in the MCP
- Handle the edge case when a connection specified in the consumer config does not exist
- Refactor how the version of the consumer module or package is determined
- Add ``ProcessingException`` as a top-level package export
- Fix misc docstrings
- Fix the use of ``SIGABRT`` being used from child processes to notify the MCP when
  processes exit, instead register for ``SIGCHLD`` in the MCP.

3.18.9
------

- Added ``rejected.testing.AsyncTestCase.published_messages`` and ``rejected.testing.PublishedMessage``
- Updated testing documentation
- Updated the setup.py extras install for testing to install all testing dependencies
- Made ``raven`` optional in ``rejected.testing``

3.18.8
------

- Fix the mocks in ``rejected.testing``

3.18.7
------

- Fix child process errors in shutdown
- Fix unfiltered connection list returned to a process, introduced in v3.18.4

3.18.6
------

- Move message age stat to Consumer, add method to override key

3.18.5
------

- Treat NotImplementedError as an unhandled exception

3.18.4
------

- Handle UNHANDLED_EXCEPTION in rejected.testing
- Add the ``rejected.consumer.Consumer.io_loop`` property
- Add the ``testing`` setup.py ``extras_require`` entry

3.18.3
------

- Fix ``rejected.consumer.Consumer.require_setting``

3.18.2
------

- Fix the republishing of dropped messages

3.18.1
------

- Fix ``ProcessingException`` AMQP header property assignment

3.18.0
------

- Add connection as an attribute of channel in ``rejected.testing``
- Refactor how error text is extracted in ``rejected.consumer.Consumer.execute``
- When a message raises a ProcessingException, the string value of the exception is added to the AMQP message headers property
- Messages dropped by a consumer can now be republished to a different exchange

3.17.4
------

- Don't start consuming until all connections are ready, fix shutdown

3.17.3
------

- Fix publisher confirmations

3.17.2
------

- Don't blow up if ``stats`` is not defined in config

3.17.1
------

- Documentation updates
- Fix the test for Consumer configuration

3.17.0
------

- ``rejected.testing`` updates
- Add automatic assignment of ``correlation-id`` to ``rejected.consumer.Consumer``
- Only use ``sentry_client`` if it’s configured
- Behavior change: Don't spawn a process per connection, Spawn ``qty`` consumers with N connections
- Add State.is_active
- Add attributes for the connection the message was received on and if the message was published by the consumer and returned by RabbitMQ
- Deprecate ``PublishingConsumer`` and ``SmartPublishingConsumer``, folding them into ``Consumer`` and ``SmartConsumer`` respectively
- Refactor to not have a singular channel instance, but rather a dict of channels for all connections
- Add the ability to specify a channel to publish a message on, defaulting to the channel the message was delivered on
- Add a property that indicates the current message that is being processed was returned by RabbitMQ
- Change ``Consumer._execute`` and ``Consumer._set_channel`` to be “public” but will hide from docs.
- Major Process refactor
    - Create a new Connection class to isolate direct AMQP connection/channel management from the Process class.
    - Alter Process to allow for multiple connections. This allows a consumer to consume from multiple AMQP broker connections or have AMQP broker connections that are not used for consuming. This could be useful for consuming from one broker and publishing to another broker in a different data center.
    - Add new ``enabled`` flag in the config for statsd and influxdb stats monitoring
    - Add a new behavior that puts pending messages sent into a ``collections.deque`` when a consumer is processing instead of just blocking on message delivery until processing is done. This could have a negative impact on memory utilization for consumers with large messages, but can be controlled by the ``qos_prefetch`` setting.
    - Process now sends messages returned from RabbitMQ to the Consumer
    - Process now will notify a consumer when RabbitMQ blocks and unblocks a connection

3.16.7
------

- Allow for any AMQP properties when testing

3.16.6
------

- Refactor and cleanup Sentry configuration and behavior

3.16.5
------

- Fix InfluxDB error metrics

3.16.4
------

- Update logging levels in ``rejected.consumer.Consumer._execute``
- Set exception error strings in per-request measurements

3.16.3
------

- Better exception logging/sentry use in async consumers

3.16.2
------

- Fix a bug using -o in Python 3

3.16.1
------

- Add ``rejected.consumer.Consumer.send_exception_to_sentry``

3.16.0
------

- Add ``rejected.testing`` testing framework

3.15.1
------

- Ensure that message age is always a float

3.15.0
------

- Sentry Updates
    - Catch all top-level startup exceptions and send them to sentry
    - Fix the sending of consumer exceptions to sentry

3.14.0
------

- Cleanup the shutdown and provide way to bypass cache in active_processes
- If a consumer has not responded back with stats info after 3 attempts, it will be shutdown and a new consumer will take its place.
- Add the consumer name to the extra values for logging

3.13.4
------

- Properly handle finishing in ``rejected.consumer.Consumer.prepare``
- Fix default/class level config of error exchange, etc

3.13.3
------

- Fix ``rejected.consumer.Consumer.stats_track_duration``

3.13.2
------

- Better backwards compatibility with ``rejected.consumer.Consumer`` "stats" commands

3.13.1
------

- Bugfixes:
    - Construct the proper InfluxDB base URL
    - Fix the mixin __init__ signature to support the new kwargs
    - Remove overly verbose logging

3.13.0
------

- Remove Python 2.6 support
- Documentation Updates
- consumer.Consumer: Accept multiple MESSAGE_TYPEs.
- PublishingConsumer: Remove routing key from metric.
- Add per-consumer sentry configuration
- Refactor Consumer stats and statsd support
- Update to use the per-message measurement
    - Changes how we submit measurements to statsd
      - Drops some redundant measurements that were submitted
      - Renames the exception measurement names
    - Adds support for InfluxDB
