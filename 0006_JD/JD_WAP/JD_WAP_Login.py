import requests
import traceback
import rsa
import base64
import binascii
import md5

class Login():
    def __init__ (self):
        self.Session = requests.Session()
        self.Session.headers.update({'User-Agent' :
                                     'Mozilla/5.0 (Linux; Android 5.1; MZ-m2 note Build/LMY47D) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/45.0.2454.94 Mobile Safari/537.36'})
        #self.Session.proxies = {'http': '127.0.0.1:9690', 'https': '127.0.0.1:9690'}

    def GetLoginInfo (self,RsaStr,KenStr):
        '''
            risk_jd[token]  MTD3HFF2BI2JHDMKFTUFGLABFTONT66KV62FB5IWAV2YHBBLFQAJYE62FHGO5PNPLPGMCYSHAWWUY
            risk_jd[eid]    0A63FD55CEB5B2BEC8FC5C0727EE62DE6E416E0AB7DD8C10F1153D21EA709E58D45BE365A98F811666D7A9A2C6C0D586
            risk_jd[fp] 420a740741365c39451ccdc429039513
            risk_jd[sid]
        '''
        LoginInfo = {
            'username' : '15806030805',
            'remember' : 'true',
            's_token' : KenStr,
            }
        bin
        PublicKey = rsa.PublicKey(int(RsaStr,16),65537)
        pwd = rsa.encrypt('cqf881211',PublicKey)

        LoginInfo['pwd'] = 'xxx'
        LoginInfo['dat'] = 'xxx'
        LoginInfo['authcode'] = 'xxx'
    def Plogin (self):
        def FindVar (str):
            ret = str.split("'")
            return ret[1]
        def GetData (str,userName,Password):


        try:
            #we will get some login var from m.jd.com
            r = self.Session.get('http://m.jd.com')
            r = self.Session.get('https://passport.m.jd.com/user/login.action?returnurl=http://m.jd.com?indexloc=1')
            RsaStrIndex = r.text.find('str_rsaString')
            KenStrIndex = r.text.find('str_kenString')
            getDataFuncIndex = r.text.find('getDat')

            if RsaStrIndex < 0 or KenStrIndex < 0 or getDataFuncIndex < 0:
                print 'Not find str_rsaString or str_kenString or getDataFuncIndex'
                return False
            RsaStr = FindVar(r.text[RsaStrIndex:RsaStrIndex + 300])
            KenStr = FindVar(r.text[KenStrIndex:KenStrIndex + 30])
            r
            DatStr = GetData(r.text[getDataFuncIndex:getDataFuncIndex + 300],userName,Password)
            print '111',RsaStr,'222',KenStr,'111'
            #r = self.Session.get('https://plogin.m.jd.com/cgi-bin/m/authcode?mod=login')
            #with open('a.png','wb') as f:
            #    f.write(r.content)
            #    f.close()

            return True
        except Exception as e:
            print e.message, traceback.format_exc()
            return False



if __name__ == '__main__':
    #tt = Login()
    #tt.Plogin()
    #14qkfl3e
    #pubk = int('BA65A1ADD9D0FB2874FD18650387A1E2E8C1B08312111DBD5404BA14CCB2B4426347B17D6F3AE4A1A36A8A8CDB612ACD88181C1971222516C1618A48403D3776CA7BE72EB148C183363ADE81635E4FBE7168C55F25EC1EDD3AA9F5509B1E83C92037313F868F9D239FE1D5676C1D52443259C5B50AAD22D384DF36EDEB553C4B',16)
    #print pubk
    #PublicKey = rsa.PublicKey(pubk,3)
    #print binascii.b2a_hex('BA65A1ADD9D0FB2874FD18650387A1E2E8C1B08312111DBD5404BA14CCB2B4426347B17D6F3AE4A1A36A8A8CDB612ACD88181C1971222516C1618A48403D3776CA7BE72EB148C183363ADE81635E4FBE7168C55F25EC1EDD3AA9F5509B1E83C92037313F868F9D239FE1D5676C1D52443259C5B50AAD22D384DF36EDEB553C4B')
    #pwd = rsa.encrypt('cqf881211',PublicKey)
    #print binascii.b2a_hex(pwd)
    #print base64.b64encode(pwd)
    #ljF2rhR7stULKuFmSKJn0fQlYjOohffj5KBSU8W0Uaz8HQ1M0Pym8wJo9jNKnQoixhkN14GR+kV1mdAOvcGOcbCcS9+tCkB1mtTfUlC036tUoWVDm4NS6E9JVY1Q/et9DiYV7lgF2j/jRwMmz5nM6+G4rKwYqCV1orrZxdFD9CE=
    md5sum = md5.new()
    md5sum.update('15806030805' + 'ljF2rhR7stULKuFmSKJn0fQlYjOohffj5KBSU8W0Uaz8HQ1M0Pym8wJo9jNKnQoixhkN14GR+kV1mdAOvcGOcbCcS9+tCkB1mtTfUlC036tUoWVDm4NS6E9JVY1Q/et9DiYV7lgF2j/jRwMmz5nM6+G4rKwYqCV1orrZxdFD9CE=' + 'c$xg^97grPo*dStF')
    print md5sum.hexdigest()
