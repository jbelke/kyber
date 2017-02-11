import signal


class TimedOutExc(Exception):
    pass


def handler(signum, frame):
    raise TimedOutExc()


def validate_asset(transaction, bigchain):
    try:
        if not hasattr(transaction, 'asset'):
            raise KeyError('asset not found in transaction {}'.format(transaction))

        asset = transaction.asset
        if 'id' in asset:
            create_tx, _ = bigchain. \
                get_transaction(asset['id'], include_status=True)
            asset = create_tx.asset

        if 'data' in asset:
            asset_data = asset['data']
            if 'script' in asset_data:
                script = asset_data['script']
                try:
                    # time out after 1 second
                    signal.signal(signal.SIGALRM, handler)
                    signal.alarm(1)
                    # do not allow builtins or other funky business
                    context = {
                        'print': print,
                        'len': len
                    }
                    exec(script, {"__builtins__": context}, {'bigchain': bigchain})
                    signal.alarm(0)
                    return True

                except Exception as e:
                    raise Exception('Asset code evaluation failed with {} : {}'
                                    .format(e.__class__.__name__, e).rstrip())
        else:
            raise KeyError('no data or id in asset')
    except Exception as e:
        print(e)
        return False
