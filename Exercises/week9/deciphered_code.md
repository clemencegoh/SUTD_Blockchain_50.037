https://ethervm.io/decompile

```
contract Contract {
    function main() {
        memory[0x40:0x60] = 0x80;
        var var0 = msg.value;
    
        if (var0) { revert(memory[0x00:0x00]); }
    
        storage[0x00] = msg.sender | (storage[0x00] & ~0xffffffffffffffffffffffffffffffffffffffff);
        memory[0x00:0x013f] = code[0x60:0x019f];
        return memory[0x00:0x013f];
    }
}

```


