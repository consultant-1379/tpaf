package com.ericsson.procus.tpaf.encryption;

import java.io.*;
import java.security.Key;
import javax.crypto.*;
import javax.crypto.spec.SecretKeySpec;

import org.apache.tools.ant.BuildException;

import java.security.Provider;
import java.security.Security;

import com.ericsson.procus.tpaf.utils.TPAFenvironment;

public class AESCrypter
{

    public AESCrypter()
    {
    }

    public Key encrypt(InputStream is, OutputStream os)
    {		
        CipherOutputStream cos = null;
        Key key = getRandomKey();
        try
        {
            Cipher cipher = Cipher.getInstance((new StringBuilder()).append(cipherName).append(cipherMethod).toString());
            cipher.init(1, key);
            cos = new CipherOutputStream(os, cipher);
            int in;
            while((in = is.read()) != -1){
                cos.write(in);
            }
            cos.close();
        }
        catch(Exception e)
        {
        	throw new BuildException(e.getMessage());
//        	System.out.println("Caught an exception while encrypting!\n");
//        	System.out.println(e.getMessage()+"\n");
//            e.printStackTrace();
//            return null;
        }
        return key;
    }

    public void decrypt(InputStream is, OutputStream os, Key key)
        throws Exception
    {
        try
        {
            Cipher cipher = Cipher.getInstance((new StringBuilder()).append(cipherName).append(cipherMethod).toString());
            cipher.init(2, key);
            CipherInputStream cis = new CipherInputStream(is, cipher);
            int in;
            while((in = cis.read()) != -1) 
                os.write(in);
        }
        catch(Exception e)
        {
            e.printStackTrace();
            throw new Exception((new StringBuilder()).append("Decryption failed: ").append(e.getMessage()).toString());
        }
    }

    public static Key getRandomKey()
    {
        return new SecretKeySpec(getRandomBytes(16), "AES");
    }

    private static byte[] getRandomBytes(int num)
    {
        if(num > 0)
        {
            byte bytes[] = new byte[num];
            for(int i = 0; i < bytes.length; i++)
                bytes[i] = (byte)(int)Math.round(Math.random() * 127D);

            return bytes;
        } else
        {
            return null;
        }
    }

    public static final String DEFAULT_CIPHER_NAME = "AES";
    public static final String DEFAULT_METHOD = "ECB";
    public static final String DEFAULT_PADDING = "PKCS5Padding";
    private final String cipherName = "AES";
    private final String cipherMethod = "/ECB/PKCS5Padding";
}
