import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives import padding


def pkcs7_padding(data):
    padder = padding.PKCS7(AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    return padded_data


def pkcs7_unpadding(data):
    unpadder = padding.PKCS7(AES.block_size).unpadder()
    unpadder_data = unpadder.update(data) + unpadder.finalize()
    return unpadder_data


def xor_encrypt(data, key, encrypt=True):
    if not encrypt:
        data = str(base64.b64decode(data), encoding="utf-8")

    index = 0
    result = ""
    for x in range(len(data)):
        result = result + chr(ord(data[x]) ^ ord(key[index]))
        index = (index + 1) % len(key)
    return str(base64.b64encode(bytes(result, encoding="utf-8")), encoding="utf-8") if encrypt else result


def xor_decrypt(data, key):
    return xor_encrypt(data, key, encrypt=False)


def md5(data, hex_result=True):
    if isinstance(data, str):
        data = data.encode("utf-8")
    m1 = hashlib.md5()
    m1.update(data)
    return m1.hexdigest() if hex_result else m1.digest()


def hash256(data, hex_result=True):
    if isinstance(data, str):
        data = data.encode("utf-8")
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest() if hex_result else h.digest()


def hash1(data, hex_result=False):
    if isinstance(data, str):
        data = data.encode("utf-8")
    h = hashlib.sha1()
    h.update(data)
    return h.hexdigest() if hex_result else h.digest()


def aesgcm_encrypt(key, nonce, aad, data):
    # print("===================aes_gcm_encrypt===================")
    # print("key:" + bytes.hex(key))
    # print("nonce:" + bytes.hex(nonce))
    # print("aad:" + bytes.hex(aad))
    # print("data:" + bytes.hex(data))
    # print("===================end aes_gcm_encrypt===================")
    aesgcm = AESGCM(key)
    return aesgcm.encrypt(nonce,data,aad)


def aesgcm_decrypt(key, nonce, aad, data):
    # print("===================aes_gcm_decrypt===================")
    # print("key:" + bytes.hex(key))
    # print("nonce:" + bytes.hex(nonce))
    # print("aad:" + bytes.hex(aad))
    # print("data:" + bytes.hex(data))
    # print("===================end aes_gcm_decrypt===================")
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce,data,aad)


def aesecb_encrypt(key, data):
    encryptor = Cipher(AES(bytes.fromhex(key)), modes.ECB(), default_backend()).encryptor()
    return encryptor.update(pkcs7_padding(data))


def aesecb_decrypt(key, data):
    decryptor = Cipher(AES(bytes.fromhex(key)), modes.ECB(), default_backend()).decryptor()
    return pkcs7_unpadding(decryptor.update(data))


def aescbc_encrypt(key, vector, data):
    encryptor = Cipher(AES(key), modes.CBC(vector), default_backend()).encryptor()
    return encryptor.update(pkcs7_padding(data))


def aescbc_decrypt(key, vector, data):
    decryptor = Cipher(AES(key), modes.CBC(vector), default_backend()).decryptor()
    return pkcs7_unpadding(decryptor.update(data))


def mystr_aesgcm(data, op):
    key = bytes.fromhex("c75ed3f33f961f55fc79de3163f349b9c75ed3f33f961f55fc79de3163f349b9")
    nonce = b"my_aesgcm_nonce"
    aad = b'my_aesgcm_aad'

    if op == "encrypt":
        ed = aesgcm_encrypt(key, nonce, aad, data.encode("utf-8"))
        return bytes.hex(ed)
    elif op == "decrypt":
        dd = aesgcm_decrypt(key, nonce, aad, bytes.fromhex(data))
        return str(dd, encoding="utf-8")
    else:
        raise Exception("op error")


def ecdh_gen_key_pair(curve=ec.SECP256R1):
    private_key = ec.generate_private_key(curve, default_backend())
    public_key = private_key.public_key()
    return private_key, public_key


def ecdh_serialize_private_key_bytes(
        private_key,
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()):
    return private_key.private_bytes(
        encoding=encoding,
        format=format,
        encryption_algorithm=encryption_algorithm
    )


def ecdh_serialize_public_key_bytes(
        public_key,
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint):
    return public_key.public_bytes(
        encoding=encoding,
        format=format
    )


def ecdh_load_der_private_key(data, password=None, backend=default_backend()):
    return serialization.load_der_private_key(data, password, backend)


def ecdh_load_public_key_from_point(data, curve=ec.SECP256R1()):
    return ec.EllipticCurvePublicKey.from_encoded_point(curve, data)


def ecdh_compute_key(private_key, public_key):
    return private_key.exchange(ec.ECDH(), public_key)


if __name__ == "__main__":
    # payload = kwai_pb2.payloadSend()
    # payload.a = "Message.Send"
    # payload.b = 845183101
    # payload.c = 1
    # # payload.d = bytes.fromhex("10feb9e7d0e288a51c2208081a10c6de939c063208081a10ddc1c9e0063a04736431334a060a047364313392010a31383133313433373733")
    #
    # payload.d.b = 15925627770756350
    # payload.d.d.a = 26
    # payload.d.d.b = 1669656390
    # payload.d.f.a = 26
    # payload.d.f.b = 1813143773
    # payload.d.g = "sd13"
    # payload.d.i.a = "sd13"
    # payload.d.r = "1813143773"
    #
    # # payloadR = kwai_pb2.payloadR()
    # payload.g.a = "zh-cn"
    # payload.g.b = 16
    # # payload.g = payloadR.SerializeToString()

    # a = payload.SerializeToString()
    # a = bytes.fromhex("0a0e42617369632e526567697374657210acc0edee07180122f8020a630a12636f6d2e736d696c652e6769666d616b6572120b372e312e312e31323534371a0747454e455249432207332e302e382e355a150a0a73646b56657273696f6e1207332e302e382e355a170a0c696d73646b56657273696f6e1207332e302e382e35126608011a05506978656c2a18414e44524f49445f616665353531303538626535363038383218414e44524f49445f616665353531303538626535363038383a18414e44524f49445f616665353531303538626535363038384206676f6f676c654a05506978656c1a0208012001280140c6d4c8bde9adacde33508e025a93010a084b55414953484f55120d414e44524f49445f50484f4e4520da8996b1072a18414e44524f49445f6166653535313035386265353630383830818284083a0b372e312e312e31323534374203372e314a03302e305203302e305a0d676f6f676c6528506978656c296204574946496a0d414e44524f49445f372e312e32720747454e455249437a057a682d636e8201027a613a090a057a682d636e1010")

    # key = base64.b64decode("BMXDlE1c7SP3+zqOyb4pNw==")

    key = bytes.fromhex("15d9e37c6a8c24b96af131216c446709")

    enb = bytes.fromhex("d3bcd36c26aee6a075f231b4370825b5da17b2da26019840478c25d165f4cfacde5397dc17482ec835c63adc1e68fb63851f64dd2ea5bdf17233de538441c76e062f0b80bb3918d9d61b984dec9a45aecfc666cceff86ff74756ca60e7a8e33b18ef63f481d98baed881741b70e4bc929b44a03e2ed98c437f4fdeabceb8892c863c481627ab25bd9417a91d54db8755aeb9819c43803b80052dcc6b28774566601daea6e639f74bf6c9a82c2dbfc903")

    vector = enb[:16]
    print(bytes.hex(vector))

    print(bytes.hex(aescbc_decrypt(key, enb[:16], enb[16:])))
    # print(bytes.hex(vector + aescbc_encrypt(key, vector, a)))

    # pub_k = base64.b64decode("BJW8blwTMa0XLQ81sXksPOY/kVcqvS3W322sLXAZXD9mJ8ymAwcwXYSVqMOLRBbHUCHoI7bJff/nnBTLfDr4pYY=")
    # pri_k = base64.b64decode("LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFUkl5eWlLM1M5UDdIVGFLTGVHUDFLemJDQ1E5SQpMU3hFR3hhRlZFNGpuWmU2RnF3dzBKaHc1bUFxYmZXTEs2Tmk4cHV2U1Y2Q3FDK0QyS2VTM3N2cFl3PT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg==")

    # from cryptography.hazmat.primitives.asymmetric import rsa
    # rsa_prik = rsa.generate_private_key(public_exponent=65537, key_size=512, backend=default_backend())
    # rsa_pubk = rsa_prik.public_key()
    # rsa_pubk_str = rsa_pubk.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
    # print(bytes.hex(pri_k))
    # print(bytes.hex(rsa_pubk_str))

    #
    # print(bytes.hex(pri_k))
    # prik, pubk = ecdh_gen_key_pair(curve=ec.SECP256R1)
    # print(bytes.hex(ecdh_serialize_private_key_bytes(prik, encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL)))
    # serialization.load_der_private_key(pri_k, None, default_backend())
    # print(bytes.hex(ecdh_serialize_public_key_bytes(pubk)))

    # public_key = ecdh_load_public_key_from_point(pub_k)
    # prik, pubk = ecdh_gen_key_pair()
    # prik2, pubk2 = ecdh_gen_key_pair() 
    # print(ecdh_compute_key(prik, public_key))
    # print(ecdh_compute_key(prik, public_key))

    # prik = bytes.fromhex("307702010104207c72405c5099e8c5490fa5d251f8c5fd1529bb61f116c409a7dabbdfb195f1c9a00a06082a8648ce3d030107a144034200043c6274fc52d7b42e3de6374e6eedf1724ee33163c1697d06b49cc3ae9c3349aebd607e96a9d73920482dcec3928a97b35c624b623f4ce5d6ac7b467dda7f8aad")
    # pubk = bytes.fromhex("0474b7a4cae4403085ed09fe4944aa853de096d000ae108ad9b3d10450903b3b2dbb3d2ad9164cd03bc674dc1cc748be14f5843403e7d112ca501bd0017f1ce29e")
    # prik2 = serialization.load_der_private_key(prik, None, default_backend())
    # pubk2 = ecdh_load_public_key_from_point(pubk, curve=ec.SECP256R1())
    # key = ecdh_compute_key(prik2, pubk2)
    # print(bytes.hex(key))
    # print(hash256(key))

    # from cryptography.hazmat.primitives import hashes
    # from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand
    # ecdh_kdf = HKDFExpand(algorithm=hashes.SHA256(), length=0x20, info=None, backend=default_backend())
    # ecdh_agree_key = ecdh_kdf.derive(key)
    # print(bytes.hex(ecdh_agree_key))


    # h = hashlib.sha256()
    # h.update(bytes.fromhex("31"))
    # h.update(bytes.fromhex("343135"))
    # h.update(bytes.fromhex("04a8941e6d586020ea7bf1fe0c84dedf3a71ea10abc551c9ed8749dbd859934dfac5f5543bc87ebbdf03c91481d5b2f14a393f75405e2fc6b9b11ff27c763f5001"))
    # print(h.hexdigest())
    # h.update(bytes.fromhex("bd8e832f8814ee572a8875d9b6fd31c892143132d8395b074e3870204a5e00d0f8b22cf3e72b5f1f5c50504504a9ffa83eb04534d0aa520fdb3515d0b145109611596f3e37e639"))
    # print(h.hexdigest())

    # import zlib
    # d = bytes.fromhex("0a2a0a0010001a104133353361616530393337626633300020b78880b8022a0a616e64726f69642d323530001a0c2b3132303635353635383536200d2a0030003a004800520f416e64726f696420446576696365735a0c676f6f676c652d506978656c6214081012101d12e68a9bb7ffb58777aa6c1c434d196a02656e7000780082011e413335336161653039333762663330355f31353833343038373930313739880100")
    # zd = zlib.compress(d)
    # print(bytes.hex(zd))

    # import zlib
    # d = bytes.fromhex("789ce33acdc471fd3f14300aed65e2dac564936ac765139c915f1e5259906a6768a30f6773d938e7e795a4e695d8d928463bbb38863846876464162b1464e4e7a52ae495e626a5162900f9997965893999297ab1b17636fa302d5c36a14539088d60399008978d4b667141706ab29db1818d3e8ccd6513925992938a50ef09315321006c971fd82eb01910755c368ec92599f979762636fa5016d0e0d49cc44aa0fd792013418623f3419e29cd2b49c92fcf03c921385c36fed968ee040a009527e625a7a2fb002ac865a30f7483028315130783131b078300830683178704830290b6608860c8602802ca74310289098c0c2b1819763032000084e97654")
    # zd = zlib.decompress(d)
    # print(bytes.hex(zd))

    # data = bytes.fromhex("a38c1518c10cfd89c038204f304c5e4246ee55d756cf0d911f13253c6fac4e79003bce06aa7856028b108b")
    # data = bytes.fromhex("789c8555095413d71a2608429022a6582c228ef87087cc9a4942183623451605d41610ec249940c84a12501414d40a16158b8f456dc552914dabd66a2db482080fadaf609f5a2d628b56148b1b14eb42ab6f6e42fbb0a7ef3427e7e6dfee3ffff7cd776f9c0e709cdc1c5d79aec5eea9b4f79a5585d3b26a07de6dcf71e585389eb5e705388a78223be6e3e4fecd77d65046a278fd40e6aa199b9dda8d1b1f3c6f2a440807dbaf5b5d66373d2a5fab9c9f784e5fe77fe9764ee917453f4464ff94c17838cf455058401002424808bc21112d9309e44aa51221658c888465082a22099816a0b00c9613f89cbfade07de8ee34c7c9c6d5c6c3351823309a66601146ca94186c037d56907bc2768e13ad5318f52a852f4ac01cde2c273b471b9e0dcfd9895d3d6cbc2d9e871df0acf61ccb0adb788cc70894c010588860308ea342ef5f1c2526bdd26cce3230944423376bf5720a96f0472c8986c9643414c2062c86448d50c1c14679aa0087161bf572c664d21b2123930921d02c9ab6246643123e5b2651a394502412f8c22c3818f14548184548044630368db2698c22fd103f94f530d6c3a93f4dc6c671364e502cb13022c27082142008c2cec6c6246a0168ce0661ebc79a23d8a4804d9214ad6408820d08650c218085a01bc92684d4826081301ec660184358546c40a216518b55ab180deb89004098c2010018d8081593416be47aad165ac2c853757a8d3e45c598e641e13a3914151705001a8c7a500f10232c2ebe65552398c504d0109c8251310c8ffe821c808710963280081150a9b44609995333b43248499bccda0c8d19ca541a20466132403a46af035e26069935268b85432a852a93b6ac664863a01988c9349bcc462d443326c8c036d040a6541a010b0ac98d720cf08d008e10218508e54201a9844984a469012943691989e1ac1009190d938c029402825084a24d7ac0216a79af16946055a33845c2624c214608b11c13a38c151a0aa0a102ca628387613035233d436ff6077dac1678ef80630ca3587efdcc8c4ecee8cc7e5a2d4800da309c4ad1eb53340c9fd69b0c2b4cb44aa3549952f9bf1b628b7cf8d168182e0ce5676530e92a1d2c4051448022e20c13635430b28c14be91d130b489f155335926d01a8c8611d4ef5d4008b08f09fe502b6c552b8ea008820349611608e4c8382000b484095f6a0288c2442f85809c70987a697c206b001b472cece080501cfd5f6b1cd08a63948e7d75c0b59c0ddc5a0b46c72d8201ab1a17584c301c4e522b554a1570c168b8f0af4e13981017517c056da6f980203ecc7f997a3e28035313a8e589041886c0ac369884202904472d2e780e21b4a64067424481934d80ed02184c0656b500a1ccc60c808cb524fc3fee9a5936a8d79fee3662054208311c1692ec7d418ac4d0dfe933c4d94a9bafe5fc2e6cb59528984c959c51e9947a4a12151cbd744170e892a5b1d25848476b99006f6bb9379b5b345f1a3912b46c6663cba4b171e18ba257c44a23a5c171d291ac4564a3b2e1d1a1b1d22869f492e0dff733ba143fabfafc50f6a20212f4031a847176dbfcf0b8c591c1f123a52f29c1f70f8d42968740562543ffbf1f345acb6c73fe4877d6fa8bf146454720b1110b70f03b8a1cd61dc55bac2da34bb013fac170aaadc166f5582b67eb39ae169e68a396a1652adf4c927e9733ea4fa89863bb9a3ecce134706e711d7bb8bc1eae1377e46ac66c5c391ee7b95fbed7d6553c74d0a528511b774475fddbcd81798ff6fd70dffdc9b572ff6317d2beb912d3f5bde303437be4e381bc3bf51faebaf776a55e7dcff17a6bc283f88d15676b67dadd167fff5ae41e45d02469fea9dc40656ff50a8ffee9bbabaa668fb5934ca84c576e29db5216249ff45956b37750494bd20bc31aee85e6cf5ff8746fc70a6fd41bcff4f6abaee9a605f99c44aa5c4a1a36d5ee9d5091d115a0f1aef0ba105adbc4f7bb91dc1f79f95f577b12a6624c5270cc8cd8959ef757d627057fbcf16282cf17df86254897ef9a3e3e7170e3d0b4e1793f3cb5ef7d222bed72d8b7c539a828dbb46e0267d10795139b12a772e79deaadbb79407b9773ff4cfd8fad138c333a8f551c697519f63a54b83364efe3e1d6082ab1eccd5fa5cdc6d779fd05c9c9587ab86f670cef97c1a152c7d08e389e53adb053deebd0929d7c342c5c9c367ef1d69ec06984c3cfa183c3dfe8b45f7a1daac122ef057e59b276e142de6cffa74f97fffc10791e7774cc837e2e1ebde4de4cb7db9296e3c8d1f9de213d7dc7028d53a3371d9ad17762d9551167e3816e51a1fb89955d9e2babf0b0eacafddc23e70787f112bff228e1af07a7141d3bd6dab7ef6ed9f006bb1d45ae5722d2cf4e9f9916d690ec71ea49e71e87dceaadb7ae735377dedc35e980dd94d857af1da9504db9d6b2e1ad6d44e91bf6c5654b3d7dcf1c8fb799d2c1cba24fa7c1856d5d5a323cfaa4fef62ece27d92577023986f4fb1c71e7ba9a78b1b96ccddd4fa579dff964e6df3cff49a59c732a20fbe8c945417418b7d40d771bdca10ae87b7673ff259db6f1f83f9d4ee52c77103754e5552e6d4bf77b75774db3c7957f37eb661a12b7ae6b0e1cb3fba362e984b927c33fb22d48383df7454c758cadc62b577cecfcadb17d52c4bd94bb9eb3feaab971aa81345c71dd7eb1aaaef149785fe3615150b7ea95eeadd3f3a66dcf793f4c41da0da4ad5bb4604ccff1e43df17d0d7b89cb01c3f379d577a237153f7fcfffe4437b9f96ed03fde3f7e8cdbe254bcb1fa47cb5ed9592fd556b78df1d9dfca86d6fc9fd0ff22fbb38332e15dd9f467bbe1ad7e43f067d460e4c96a09199bf6d164bf8dd4586a2eac2d965aaf6c9017bc7e5ef9fa5f3dc8e14343c5773f37877e016e9f9df0ac6bdbfd27b1ca3b05f6cf34c603870e4201ecf3f129a137557667a7178a6874fdceae0a688f64b496dfb9c0f041eeecd8f0d5df8c885f3b4baabc1f6a7187ce3e54b32ac2e2cff46c1be6b49fbf51d875b6e5cfbe4cd8efba7af48337f5c1b5e5714735a5971f82bde47171e8b1764ef1e6f5b26b6cf8fb81eb276c3c0bc8bbfe6dba739240d35ad9eeee688862b77bbb77d51d3919a5652fa70f1a0fa4e767cb0eb2f8333d696e50679b9a7d8c5e7321dc593aee65035219eff08705bb1fbd61643ef3b17df28cff9b9be7659f6b939a8f871fe5065cab609d5e70692279ef87ce6fe6153bd7b7481dbad379fd61e943c7ed07aa3d350953f7752fdfcc69eb62d6f6d8a473abab2be698aa2ea760e39cfd91eb16f62396a9cb50b6fde11d9aa48e76da84f7eb8c5b7e69dd26d7b077744becb1371e967713b136bc8f68058d3cef7044d5f376eeebee458ffda19a5d7c5a1b1e9a5eeb9b72efee74679e34f92dff29b44d2b7065e6c3bef16c4cb8f7845bdf3d0d95d86b78b9f39dbd53952cb3d45499f7aa79927a72f3beabf7ad3dbea70dd63c9879ed84d657dde69e4f54bd7a7eb5a3e78deed9bb0307ee2851f37d9ba74defd5cee93af3993dabe2b64cfc3ff021bc78e78")
    # key = bytes.fromhex("6353c51d50b0626cb0446f7d88bbad001a66c8d085996e0a")
    # nonce = bytes.fromhex("e6301c5c95aea7a80d96d428")
    # aad = bytes.fromhex("5daeb9228722e74c071071c55ff0f6e395e9edfb4c95bf35f6ed809ded96757d")
    # endata = aesgcm_encrypt(key, nonce, aad, data)
    # print("endata:%s" % bytes.hex(endata))

    # data = bytes.fromhex("08696d3feeb9a3f9e6f050b90dff7122c25181cf4c3ea9421b7118e7591de0db81e39b28c8789e4c4a07aed2d79cf86903a7e6295b12955229c85dce63066fa9cf1832c3ce3f2be0bb4f9c7cd978959308e9346fc842e95f427a44a94fd2145d428e6ebe47d8ef14e005a7ee369647cbeeaf222ac9e5c7c7b6b1c09de3bb5fb3ed605ec33a417462b2673b8fa0a39ae3cb6faaa37b6bc10829c0aa356cb1f8d138923b349ef417fbc5a11f3c407366f225ef7f518c48979214bb034dd87f51d2bac5dbca71edbe8b14ec40017eb24b2a28931e1a721a93e8231c79ae0e13d997ddc2983e3034b96eb44d2b6f172de02e370f0e92fd65b3b054fac5897e2c57f45229513556120f245cbd34cd247e")
    # key = bytes.fromhex("1f67ac86a0f9db8dc40db40a75d802ae017a3ab2c048d261")
    # nonce = bytes.fromhex("93e07dc614e95b93a07d3699")
    # aad = bytes.fromhex("600c0953359f14f00c52405494d3add56aa398e5e3329ddf1d311abc0947456f")
    # endata = aesgcm_decrypt(key, nonce, aad, data)
    # print("endata:%s" % bytes.hex(endata))


    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand
    from cryptography.hazmat.primitives.hmac import HMAC

    # key = b"security hdkf expand"
    # key_material = bytes.fromhex("1e438982352a9878d13818addfecbf25d8884a668a9f0842470ad694f02a795c")
    # h = HMAC(algorithm=hashes.SHA256(), key=key, backend=default_backend())
    # h.update(key_material)
    # key_result = h.finalize()
    # print(bytes.hex(key_result))

    # info = b"security hdkf expand"
    # info = bytes.fromhex("1677d8017c7ed03d73915915c4a68b6c85d4f449694386b7dbd9bfb461e7dc41")
    # key = bytes.fromhex("73c26dddfb03aa8006669054490895378056705eb107ff9f41c478636f5aa2cc")
    # salt = bytes.fromhex("2a05bb4a933ce74c000e078725a91dbcaaab50912726373f55e5d97e03e98b5e")
    # # info = info + info2
    # ecdh_kdf = HKDFExpand(
    #     algorithm=hashes.SHA256(), 
    #     length=56, 
    #     info=info,
    #     backend=default_backend())
    # ecdh_agree_key = ecdh_kdf.derive(key)
    # print(bytes.hex(ecdh_agree_key))


    # import os, sys
    # project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # project_name = os.path.basename(os.path.normpath(project_path))
    # sys.path.insert(0, project_path)
    # from app.protobuf import mm_pb2
    # d = mm_pb2.HybridEcdhEncryptData(
    #     unknown1=1,
    #     ecdh=mm_pb2.HybridEcdhEncryptData.ECDH(
    #         nid=415,
    #         pubkey=bytes.fromhex("0467459f4c5988819f0a97c2b83fe45cd3e353047397079758d7e255f28a49bbe6449821838e6e243c6d67c54781555e9a05d6bd88f39fffb4d159b04c0b0e9ff8")
    #     ),
    #     client_en_data1=bytes.fromhex("10d38d06c9926edcbcfa06b22c3f3dc51cfd8eea66f0862a075dfcd60f25aae12c1ff46a2b02bea32df1e33c24a5377cad9b9ca61009a34f727e184a3f8f804d14df2bd10e"),
    #     unknown4=b"",
    #     client_en_data2=bytes.fromhex("0be77e43ed49bf37ea9901885a05b44b34f0d6196bbdd5e769716e1b458d33f73cdea27dd7c31d96167e0ef3aad6f0c84613059cd0a8f17c8f45aa677cf3e7b9073fc15546e385118b93c6957a9bf9e81df9bb984e539b554534fe20c15b5d29562e4d7803b9140e264b936b92b23b89d81c072fc4990836731ee7c6857041c5ff989a7c8b43a7af44117e82ea4ed91ce76b47c3eb9c5d50e09c3fb38aa1c9907292a1393b0a3cd7eafe099a3e532636ef93d9c175944f5691") 
    # )
    # print(bytes.hex(d.SerializeToString()))

    # server_data = bytes.fromhex("0a46089f0312410474b7a4cae4403085ed09fe4944aa853de096d000ae108ad9b3d10450903b3b2dbb3d2ad9164cd03bc674dc1cc748be14f5843403e7d112ca501bd0017f1ce29e10011a9a024d40b0a7616a0a51e9d38a05bd9ed35b33864b22b76a64c8760596913ca20c9e1a87e36b84d15155b11e4761b0269dd2003bcadaae8acd9d2be5568c02e9bc845b30293fc4fde2be98f68cf115129df7f0fd4c5cec0ee0096712efe50f66405f1d3f18bf75f47331ccdf507a5b18e5ef85b39e34c1bd2a8998556972c40b009ace12ea6ee03daf4441b072d516551a220532ecdfb747d7c4dd3c93a53f4d284aa9176d9ed16490a71e3a93208c8e3eb86de5137a245e0d36109708d82c74ce7f0f6744c7070183f4a2abe9ed11f7eda2c14565ef79124e1d176093bfb5e695b57f0456ff3afbd5a382a166190ae4cee29ba93e80ecc1592cd0973cae468cbe383cbbcaf79f1126419c66a523f5d3dcf5522fe8912c55010c5a1a224630440220294f43ff958d3a54ab558fe078c78785445d16bf6da491eb9b08f2fe42371762022004c30153e378e0b287eabf050eacfd96d1193696943277c00ebc6f82b0e791b3")
    # pb = mm_pb2.HybridEcdhDecryptData()
    # pb.ParseFromString(server_data)
    # print("nid: %s" % pb.ecdh.nid)
    # print("server_pub_k1: %s" % bytes.hex(pb.ecdh.pubkey))
    # print("server_en_data1: %s" % bytes.hex(pb.server_en_data1))
    # print("server_en_data2: %s" % bytes.hex(pb.server_en_data2))

    # d = bytes.fromhex("3e956cf79632aaceff95ecb5187a6e7397dc0d8f7857247c491dfc93e74c4cd70ef31834c9ef92b18ef05f1dd066056d514fc8765b08bb4e8c2003be6ccfbc9c239a3eee1834705cad350ddd46e70b28d29945cfb87064553bd4a768ccf3518b05b9ce2bff7b533bdaaaa9e428b37842")
    # print(md5(d))

