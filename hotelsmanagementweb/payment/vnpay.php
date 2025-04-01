<?php
class VNPay {
    private $vnp_TmnCode = ""; // Merchant ID
    private $vnp_HashSecret = ""; // Hash Secret
    private $vnp_Url = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"; // Payment URL
    private $vnp_ReturnUrl = "http://localhost:3000/payment/vnpay_return.php"; // Return URL

    public function createPaymentUrl($amount, $orderId, $orderInfo) {
        $vnp_TxnRef = $orderId; // Mã tham chiếu giao dịch
        $vnp_OrderInfo = $orderInfo; // Thông tin mô tả nội dung thanh toán
        $vnp_Amount = $amount * 100; // Số tiền thanh toán (nhân với 100)

        $vnp_Locale = 'vn'; // Ngôn ngữ
        $vnp_IpAddr = $_SERVER['REMOTE_ADDR']; // IP của khách hàng
        $vnp_CreateDate = date('YmdHis'); // Thời gian tạo giao dịch

        $inputData = array(
            "vnp_Version" => "2.1.0",
            "vnp_TmnCode" => $this->vnp_TmnCode,
            "vnp_Amount" => $vnp_Amount,
            "vnp_Command" => "pay",
            "vnp_CreateDate" => $vnp_CreateDate,
            "vnp_CurrCode" => "VND",
            "vnp_IpAddr" => $vnp_IpAddr,
            "vnp_Locale" => $vnp_Locale,
            "vnp_OrderInfo" => $vnp_OrderInfo,
            "vnp_OrderType" => "other",
            "vnp_ReturnUrl" => $this->vnp_ReturnUrl,
            "vnp_TxnRef" => $vnp_TxnRef
        );

        if (isset($vnp_BankCode) && $vnp_BankCode != "") {
            $inputData['vnp_BankCode'] = $vnp_BankCode;
        }

        ksort($inputData);
        $query = "";
        $i = 0;
        $hashdata = "";
        foreach ($inputData as $key => $value) {
            if ($i == 1) {
                $hashdata .= '&' . urlencode($key) . "=" . urlencode($value);
            } else {
                $hashdata .= urlencode($key) . "=" . urlencode($value);
                $i = 1;
            }
            $query .= urlencode($key) . "=" . urlencode($value) . '&';
        }

        $vnp_Url = $this->vnp_Url . "?" . $query;
        if (isset($this->vnp_HashSecret)) {
            $vnpSecureHash = hash_hmac('sha512', $hashdata, $this->vnp_HashSecret);
            $vnp_Url .= 'vnp_SecureHash=' . $vnpSecureHash;
        }

        return $vnp_Url;
    }

    public function validatePayment($vnp_ResponseCode) {
        if ($vnp_ResponseCode == "00") {
            return true;
        }
        return false;
    }
}
?> 