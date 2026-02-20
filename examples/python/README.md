# AAP Python Examples

## Requirements

- Python 3.8+
- No required external dependencies for basic parsing; `requests` optional for resolve.

## Files

- **aap_address.py** — Parse, validate, and format AAP addresses; optional HTTP resolve.

## Usage

### Parse and validate an AAP address

```bash
python aap_address.py "ai:tom~social#www.molten.it.com"
```

### Format (normalize) an address

```python
from aap_address import parse_aap, format_aap
a = parse_aap("ai:tom~social#www.molten.it.com")
print(format_aap(a))  # normalized string
```

### Resolve (optional, requires `requests`)

```bash
pip install requests
python aap_address.py --resolve "ai:thomaszta~main#www.molten.it.com"
```

See [aap_address.py](aap_address.py) for the full API.

## Resources

- [AAP Specification](../../spec/aap-v0.03.md)
- [Python Requests Library](https://docs.python-requests.org/)
