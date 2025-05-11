import socket
import threading
import concurrent.futures
import time
import datetime
import requests
import psutil
from tqdm import tqdm
import sys
import os
import errno
import json

# --- Cấu hình ---
DEFAULT_MAX_PORT = 1024
# DEFAULT_MAX_PORT = 65535
DEFAULT_TIMEOUT_SOCKET = 0.5
DEFAULT_MAX_THREADS = 100
DEFAULT_SCAN_TYPE = "TCP_CONNECT"

# --- Banner Rồng ---
DRAGON_BANNER = r"""
                                                       ,--.
                                                      {    }
                                                      K,   }
                                                     /  `Y`
                                                _   /   /
                                               {_'-K.__/
                                                 `/-.__L._
                                                 /  ' /`\_}
                                                /  ' /     --.
                                               (`    `.      //
                                                `     )     //
                                               (      (     /)
                                                `      `    (
                                                  `  |    @ )
                                                   |      _@
                                                  |      /
                                                 |    |
                                                 |    /
                                                 |   /
                                                 (  (
                                                  `  '.
                                                   `   '.
                                                 `    '.
                                                  `     '.
                                                   `      '.
                                                 .        `
                                                .           `
                                               .             `
                                              .               `
                                             .                 `
                                            .                   `
                                           .                     `
                                          .                       .
              ____                       .                         .
     ___----~~    ~~----___             .                           .
~~~ ~~~                ~~~ ~~~----------                           .
                               ..                                  .`
                             .'  `                                   `
                            .     .                                 `
                           .    .'                                  `
                           .   .                                    `
                          .   .                                     `
                          .  .                                      `
                         .  .                                       `
                         . .                                        `
                        . .                                         `
                        ..                                          `
                       .                                            `
                      .                                             `
                     .                                              `
                    .                                               `
                   .                                                `
          ULTIMATE PORT ASSURANCE SUITE by @atty525 - DRACONIC MAJESTY EDITION
"""

def display_intro_animation():
    text_to_flash = "@atty525"
    duration = 1.5
    interval = 0.075

    rainbow_colors_bg = [
        "\033[48;2;255;0;0m",    # Red BG
        "\033[48;2;255;165;0m",  # Orange BG
        "\033[48;2;255;255;0m",  # Yellow BG
        "\033[48;2;0;255;0m",    # Green BG
        "\033[48;2;0;0;255m",    # Blue BG
        "\033[48;2;75;0;130m",   # Indigo BG
        "\033[48;2;238;130;238m",# Violet BG
    ]
    # Flashing text color (e.g., bright white or black, depending on BG for contrast)
    text_color_bright = "\033[97;1m" # Bright White
    text_color_dark = "\033[30;1m" # Bright Black for light backgrounds like yellow

    reset_format = "\033[0m"
    start_time = time.time()
    color_idx = 0
    visible = True

    try:
        terminal_width = os.get_terminal_size().columns
    except OSError: # Fallback if running in a non-terminal environment
        terminal_width = 80 
        
    padding = " " * ((terminal_width - len(text_to_flash) - 2) // 2) # -2 for spaces around text

    num_steps = int(duration / interval)

    for _ in range(num_steps):
        if time.time() - start_time > duration:
            break

        current_bg_color = rainbow_colors_bg[color_idx % len(rainbow_colors_bg)]
        
        # Choose text color for contrast
        # Simple heuristic: if background is yellow, use dark text. Otherwise bright.
        txt_color = text_color_dark if "255;255;0m" in current_bg_color else text_color_bright

        if visible:
            display_string = f"{padding}{current_bg_color}{txt_color} {text_to_flash} {reset_format}{padding}"
            sys.stdout.write(f"\r{display_string.ljust(terminal_width)}")
        else:
            sys.stdout.write(f"\r{' ' * terminal_width}")
        
        sys.stdout.flush()
        
        visible = not visible
        if visible: # Change color when it's about to become visible again
            color_idx += 1
            
        time.sleep(interval)

    sys.stdout.write(f"\r{' ' * terminal_width}\r") 
    sys.stdout.flush()
    # os.system('cls' if os.name == 'nt' else 'clear') # Optional: Clear screen

def display_banner():
    print("\033[95m" + DRAGON_BANNER + "\033[0m")

def get_ip_info(ip_address):
    print("\033[1;34m[i] Đang thực hiện truy vấn Dữ liệu Định danh Mạng Nâng cao...\033[0m")
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query,reverse")
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'success':
            print("\033[94m" + f"[🌐] Hồ sơ Chi tiết về Thực thể Mạng [{data.get('query', ip_address)}]:" + "\033[0m")
            print(f"  🗺️  Khu vực Địa lý Định vị: {data.get('city', 'Không tiết lộ')}, {data.get('regionName', 'Không tiết lộ')}, {data.get('country', 'Bảo mật')} ({data.get('countryCode', 'N/A')})")
            print(f"  📍 Tọa độ Ước lượng (Latitude/Longitude): {data.get('lat', 'N/A')} / {data.get('lon', 'N/A')}")
            print(f"  🕰️ Múi giờ Hoạt động: {data.get('timezone', 'Không xác định')}")
            print(f"  📡 Đơn vị Cung cấp Dịch vụ Liên kết Mạng (ISP): {data.get('isp', 'Không xác định')}")
            print(f"  🏢 Tổ chức Điều hành Chính: {data.get('org', 'Không xác định')}")
            print(f"  🏷️ Số hiệu Hệ thống Tự quản (AS - Autonomous System): {data.get('as', 'N/A')}")
            if data.get('reverse'):
                print(f"  🔄 Định danh Phân giải Ngược (rDNS): {data.get('reverse')}")
            print("-" * 70)
            return data
        else:
            print(f"\033[91m[⚠️] Thất bại trong việc thu thập dữ liệu định danh cho {ip_address}: {data.get('message', 'Sự cố không xác định')}\033[0m")
            return None
    except requests.exceptions.RequestException as e:
        print(f"\033[91m[❌] Sự cố trong Giao thức Truyền thông với Dịch vụ Phân giải IP: {e}\033[0m")
        return None
    except Exception as e:
        print(f"\033[91m[💥] Ngoại lệ không lường trước xảy ra trong quá trình truy vấn thông tin IP: {e}\033[0m")
        return None

def check_port_tcp_connect(target_ip, port, timeout):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                return port, "OPEN", None
            elif result == errno.ECONNREFUSED:
                return port, "CLOSED", None
            elif result == errno.ETIMEDOUT or result == errno.EHOSTUNREACH or result == errno.ENETUNREACH:
                return port, "FILTERED", None
            return port, "FILTERED", f"Mã lỗi hệ thống: {result}"
    except socket.timeout:
        return port, "FILTERED", "Vượt ngưỡng thời gian chờ kết nối"
    except socket.error as e:
        return port, "FILTERED", f"Lỗi Socket: {e.strerror}"
    return port, "UNKNOWN", "Trạng thái không xác định do lỗi bất ngờ"

def get_service_banner(target_ip, port, timeout):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((target_ip, port))
            if port == 80 or port == 8080: # HTTP
                s.sendall(b"HEAD / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\nUser-Agent: PortScanner\r\nConnection: close\r\n\r\n")
            elif port == 21: # FTP
                 pass # FTP banner is usually sent on connect
            elif port == 22: # SSH
                 pass # SSH banner is usually sent on connect
            
            banner_bytes = s.recv(1024)
            # Cố gắng decode với nhiều encoding phổ biến nếu UTF-8 thất bại
            encodings_to_try = ['utf-8', 'latin-1', 'ascii']
            banner_str = None
            for enc in encodings_to_try:
                try:
                    banner_str = banner_bytes.decode(enc).strip()
                    break 
                except UnicodeDecodeError:
                    continue
            return banner_str if banner_str else "[Dữ liệu nhị phân hoặc không thể giải mã]"
    except socket.timeout:
        return "[Timeout khi thu thập banner]"
    except socket.error:
        return "[Lỗi socket khi thu thập banner]"
    except Exception:
        return "[Không thể thu thập banner]"
    return None


def get_system_stats():
    cpu_usage = psutil.cpu_percent(interval=None)
    ram_usage = psutil.virtual_memory().percent
    return f"CPU: {cpu_usage:.1f}% Hiệu suất | RAM: {ram_usage:.1f}% Phân bổ"

def port_scanner(target_ip, start_port=1, end_port=DEFAULT_MAX_PORT, scan_type=DEFAULT_SCAN_TYPE, timeout=DEFAULT_TIMEOUT_SOCKET, num_threads=DEFAULT_MAX_THREADS):
    scan_results = {
        "target_entity": target_ip,
        "scan_initiation_timestamp": datetime.datetime.now().isoformat(),
        "scan_protocol_type": scan_type,
        "port_enumeration_scope": f"{start_port}-{end_port}",
        "per_port_timeout_threshold": timeout,
        "concurrent_threads_deployed": num_threads,
        "enumerated_ports_details": []
    }
    
    ports_to_scan = list(range(start_port, end_port + 1))
    total_ports = len(ports_to_scan)
    
    print(f"\033[93m[🚀] Khởi động Chiến dịch Thăm dò Toàn diện {total_ports} Cổng Dịch vụ trên Thực thể Mạng {target_ip} (Phạm vi: {start_port} đến {end_port}).\033[0m")
    print(f"\033[93m[⚙️] Áp dụng Kỹ thuật: {scan_type}. Huy động tối đa {num_threads} luồng xử lý song song. Ngưỡng chờ nghiêm ngặt: {timeout} giây/cổng.\033[0m")
    
    start_time_scan_process = time.time()
    
    timestamp_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_target_ip = target_ip.replace('.', '_').replace(':', '_')
    output_base_filename = f"report_scan_{safe_target_ip}_{scan_type.lower()}_{timestamp_str}"
    output_txt_filename = output_base_filename + ".txt"
    output_json_filename = output_base_filename + ".json"

    open_ports_details = []
    closed_ports_count = 0
    filtered_ports_count = 0

    try:
        with open(output_txt_filename, "w", encoding="utf-8") as f_txt:
            f_txt.write(f"BÁO CÁO THẨM ĐỊNH CỔNG DỊCH VỤ\n")
            f_txt.write(f"Thực thể Mục tiêu: {target_ip}\n")
            f_txt.write(f"Thời điểm Khởi tạo: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}\n")
            f_txt.write(f"Phương thức Thăm dò: {scan_type}\n")
            f_txt.write(f"Phạm vi Cổng Khảo sát: {start_port}-{end_port}\n")
            f_txt.write(f"Ngưỡng Chờ/Cổng: {timeout}s, Số Luồng Đồng thời: {num_threads}\n")
            f_txt.write("=" * 70 + "\n\nKẾT QUẢ CHI TIẾT:\n")

            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                progress_bar_desc = f"Đang thẩm định {scan_type}"
                with tqdm(total=total_ports, unit="cổng", dynamic_ncols=True, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]", desc=progress_bar_desc) as pbar:
                    
                    future_to_port = {}
                    if scan_type == "TCP_CONNECT":
                        future_to_port = {executor.submit(check_port_tcp_connect, target_ip, port, timeout): port for port in ports_to_scan}
                    else:
                        print(f"\033[91m[❗️] Kỹ thuật quét '{scan_type}' hiện chưa được hỗ trợ trong phiên bản này.\033[0m")
                        return scan_results

                    for i, future in enumerate(concurrent.futures.as_completed(future_to_port)):
                        port_num = future_to_port[future]
                        try:
                            scanned_port, status, details = future.result()
                            port_info = {"port_number": scanned_port, "disposition": status, "diagnostic_details": details, "service_identification_banner": None}

                            if status == "OPEN":
                                service_banner = get_service_banner(target_ip, scanned_port, timeout + 0.5)
                                port_info["service_identification_banner"] = service_banner
                                open_ports_details.append(port_info)
                                
                                banner_display = f" - Nhận diện Sơ bộ: {service_banner[:50].replace(chr(10), '; ').replace(chr(13), '')}{'...' if service_banner and len(service_banner) > 50 else ''}" if service_banner else ""
                                message_txt = f"[+] Cổng {scanned_port:<5} TRẠNG THÁI: KHẢ DỤNG (OPEN){banner_display}\n"
                                pbar.write(f"\033[92m[🔑] Cổng {target_ip}:{scanned_port:<5} KHẢ DỤNG.{banner_display}\033[0m")
                                f_txt.write(message_txt)
                                f_txt.flush()
                            elif status == "CLOSED":
                                closed_ports_count += 1
                                f_txt.write(f"[-] Cổng {scanned_port:<5} TRẠNG THÁI: TỪ CHỐI (CLOSED)\n")
                            elif status == "FILTERED":
                                filtered_ports_count += 1
                                f_txt.write(f"[?] Cổng {scanned_port:<5} TRẠNG THÁI: CHE KHUẤT/LỌC (FILTERED) - {details or ''}\n")
                            
                            scan_results["enumerated_ports_details"].append(port_info)

                        except Exception as e:
                            pbar.write(f"\033[91m[💥] Ngoại lệ khi phân tích kết quả cổng {port_num}: {e}\033[0m")
                            scan_results["enumerated_ports_details"].append({"port_number": port_num, "disposition": "ERROR", "diagnostic_details": str(e)})

                        stats_str = get_system_stats()
                        pbar.set_postfix_str(f"{stats_str} | Khả dụng: {len(open_ports_details)}, Từ chối: {closed_ports_count}, Che khuất: {filtered_ports_count}")
                        pbar.update(1)
                        
                        if i % (num_threads // 2 + 1) == 0:
                             sys.stdout.flush()

    except KeyboardInterrupt:
        print("\n\033[91m[🛑] Quy trình Thăm dò đã bị gián đoạn theo Chỉ thị Người dùng.\033[0m")
        if 'executor' in locals() and executor is not None: # Check if executor was defined
            executor.shutdown(wait=False, cancel_futures=True)
    except Exception as e:
        print(f"\n\033[91m[💥] Sự cố Hệ thống Bất khả kháng đã phát sinh: {e}\033[0m")
    finally:
        end_time_scan_process = time.time()
        total_time_scan = end_time_scan_process - start_time_scan_process
        scan_results["scan_completion_timestamp"] = datetime.datetime.now().isoformat()
        scan_results["total_execution_duration_seconds"] = round(total_time_scan, 2)

        print("-" * 70)
        print(f"\033[1m[✨] Hoàn tất Chiến dịch Thẩm định Cổng Dịch vụ cho Thực thể {target_ip}!\033[0m")

        if open_ports_details:
            print(f"\033[92m  [🎯] Tổng hợp {len(open_ports_details)} Điểm Truy cập Khả dụng đã được Xác minh:\033[0m")
            for p_info in sorted(open_ports_details, key=lambda x: x['port_number']):
                banner_str = f" (Dịch vụ/Thông điệp: {p_info['service_identification_banner'][:60].replace(chr(10), '; ').replace(chr(13), '')}{'...' if p_info['service_identification_banner'] and len(p_info['service_identification_banner']) > 60 else ''})" if p_info['service_identification_banner'] else ""
                print(f"\033[92m       Cổng {p_info['port_number']}{banner_str}\033[0m")
            print(f"\033[92m      Biên bản Chi tiết đã được Lưu trữ An toàn tại: {output_txt_filename} và {output_json_filename}\033[0m")
        else:
            print(f"\033[93m  [⭕] Không phát hiện Điểm Truy cập Khả dụng nào trong Phạm vi Khảo sát Hiện hành.\033[0m")

        print(f"\033[91m  [⛔] Ghi nhận {closed_ports_count} Cổng Dịch vụ phản hồi Từ chối Kết nối Chủ động.\033[0m")
        print(f"\033[93m  [🛡️] Ghi nhận {filtered_ports_count} Cổng Dịch vụ có Dấu hiệu bị Che khuất hoặc Giới hạn Truy cập.\033[0m")

        print(f"\n    ⏳ Tổng Thời gian Hoàn thành Giao thức: {total_time_scan:.2f} giây.")
        print(f"    💻 Trạng thái Tài nguyên Hệ thống khi Kết thúc: {get_system_stats()}")
        
        try:
            with open(output_json_filename, "w", encoding="utf-8") as f_json:
                json.dump(scan_results, f_json, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"\033[91m[❗️] Lỗi khi lưu trữ biên bản JSON: {e}\033[0m")
        
        print("-" * 70)
        return scan_results


if __name__ == "__main__":
    if os.name == 'nt':
        os.system('color')
    
    display_intro_animation() # Hiệu ứng intro
    display_banner()
    
    while True:
        target_input_str = input(f"\033[96m[❓] Kính mời Quý vị cung cấp Định danh Mạng (Địa chỉ IP hoặc Tên miền) của Thực thể Mục tiêu (hoặc nhập 'q' để hoàn tất phiên làm việc):\n└───► \033[0m").strip()
        if target_input_str.lower() == 'q':
            print("\033[93m[👋] Trân trọng ghi nhận sự hợp tác của Quý vị. Kính chúc một ngày tốt lành!\033[0m")
            break
        if not target_input_str:
            print("\033[91m[⚠️] Yêu cầu Định danh Mạng không được để trống. Xin vui lòng cung cấp thông tin cần thiết.\033[0m")
            continue
        
        resolved_ip = None
        try:
            print(f"\033[1;34m[i] Đang tiến hành Phân giải Cao cấp cho Định danh '{target_input_str}'...\033[0m")
            resolved_ip = socket.gethostbyname(target_input_str)
            if resolved_ip != target_input_str:
                 print(f"\033[94m[🔗] Định danh '{target_input_str}' đã được Ánh xạ Thành công sang Địa chỉ IP: {resolved_ip}\033[0m")
            else:
                 print(f"\033[94m[🔗] Địa chỉ IP '{resolved_ip}' đã được Xác thực là Hợp lệ.\033[0m")
        except socket.gaierror:
            print(f"\033[91m[❌] Định danh Mạng '{target_input_str}' không thể Phân giải hoặc không Hợp lệ.\033[0m")
            continue
        except Exception as e:
            print(f"\033[91m[💥] Ngoại lệ Hệ thống trong Quá trình Phân giải '{target_input_str}': {e}\033[0m")
            continue

        if resolved_ip:
            get_ip_info(resolved_ip)
            
            scan_options = {
                "target_ip": resolved_ip,
                "start_port": 1,
                "end_port": DEFAULT_MAX_PORT,
                "scan_type": "TCP_CONNECT",
                "timeout": DEFAULT_TIMEOUT_SOCKET,
                "num_threads": DEFAULT_MAX_THREADS
            }
            
            print(f"\033[1;33m[!] Hệ thống sẽ tiến hành quét với các tham số mặc định. Để tùy chỉnh nâng cao, vui lòng tham khảo tài liệu hoặc các phiên bản tương lai.\033[0m")
            port_scanner(**scan_options)
        
        print("-" * 70)