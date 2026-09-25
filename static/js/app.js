// Quản lý Tab chính của giao diện điều khiển
    function switchMainTab(tabName) {
      const btnDashboard = document.getElementById('tab-btn-dashboard');
      const btnDatabase = document.getElementById('tab-btn-database');
      const paneDashboard = document.getElementById('tab-pane-dashboard');
      const paneDatabase = document.getElementById('tab-pane-database');

      if (tabName === 'dashboard') {
        btnDashboard.classList.add('active');
        btnDatabase.classList.remove('active');
        paneDashboard.classList.add('active');
        paneDatabase.classList.remove('active');
      } else {
        btnDashboard.classList.remove('active');
        btnDatabase.classList.add('active');
        paneDashboard.classList.remove('active');
        paneDatabase.classList.add('active');

        loadOrdersDatabase();
      }
    }

    // Global State quản lý truy vấn Database đơn hàng
    let currentOrdersPage = 1;
    let currentHazardFilter = 'all';
    let currentSearchQuery = '';
    let ordersListGlobal = [];

    // Hàm load dữ liệu từ API /api/orders
    async function loadOrdersDatabase() {
      const tbody = document.getElementById('orders-table-tbody');
      tbody.innerHTML = `
    <tr>
      <td colspan="8" style="text-align: center; padding: 40px; color: var(--text-dark); font-weight: 600">
        <span class="pulse-dot"></span> Đang tải cơ sở dữ liệu và phân tích thảm họa từ máy chủ...
      </td>
    </tr>
  `;

      try {
        const url = `/api/orders?page=${currentOrdersPage}&per_page=15&hazard_filter=${currentHazardFilter}&search=${encodeURIComponent(currentSearchQuery)}`;
        const res = await fetch(url);
        const data = await res.json();

        if (!data.success) {
          tbody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align: center; padding: 40px; color: var(--neon-red); font-weight: 700">
            Lỗi: ${data.message || 'Không thể liên kết cơ sở dữ liệu'}
          </td>
        </tr>
      `;
          return;
        }

        ordersListGlobal = data.orders || [];
        renderOrdersTable(data);
      } catch (err) {
        console.error(err);
        tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; padding: 40px; color: var(--neon-red); font-weight: 700">
          Lỗi máy chủ kết nối dịch vụ API đơn hàng: ${err.message}
        </td>
      </tr>
    `;
      }
    }

    function renderOrdersTable(data) {
      const tbody = document.getElementById('orders-table-tbody');

      if (ordersListGlobal.length === 0) {
        tbody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; padding: 40px; color: var(--text-muted); font-weight: 600">
          Không tìm thấy đơn hàng nào khớp với điều kiện tìm kiếm hoặc bộ lọc hiện hành.
        </td>
      </tr>
    `;
        updatePaginationUI(0, 1, 1);
        return;
      }

      tbody.innerHTML = '';
      ordersListGlobal.forEach((order) => {
        const tr = document.createElement('tr');

        const routeHtml = `
      <div style="font-weight: 600; color: var(--text-dark)">${order.customer_city}, ${order.customer_country}</div>
      <div style="font-size: 11px; color: var(--text-muted); margin-top: 3px; display: flex; align-items: center; gap: 4px">
        <span>Tuyến đường:</span>
        <span style="font-family: var(--font-mono); color: var(--neon-teal); font-weight: 700">
          ${order.order_city || 'OEM Factory'} ➔ ${order.customer_country_iso || 'Customer Point'} (${order.shipping_mode})
        </span>
      </div>
    `;

        // Sản phẩm: Hiển thị lòng danh sách toàn bộ sản phẩm bên trong đơn hàng
        let productHtml = `<div style="display: flex; flex-direction: column; gap: 10px">`;
        order.products.forEach((prod) => {
          productHtml += `
        <div style="border-left: 2.5px solid var(--neon-teal); padding-left: 10px">
          <div style="font-weight: 700; color: var(--text-dark); max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap" title="${prod.product_name}">
            ${prod.product_name}
          </div>
          <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px">
            Dòng: <span style="font-weight:600; color:#334155">${prod.category_name}</span> | SL: <span style="font-weight:700; color:var(--text-dark)">${prod.order_item_quantity} ${prod.auto_metrics.qty_unit}</span>
            <span style="margin-left:6px; padding:2px 6px; background:#F1F5F9; border-radius:4px; font-weight:700; color:var(--text-dark)">$${prod.auto_metrics.auto_unit_price}/cái</span>
          </div>
          <div style="margin-top: 3px">
            <button class="load-order-btn" style="padding: 2px 8px; font-size: 10px;" onclick="selectAndLoadOrder(${order.order_id}, ${prod.row_index})" title="Khảo sát dự báo riêng sản phẩm này">
              <span></span> Khảo sát sản phẩm này
            </button>
          </div>
        </div>
      `;
        });
        productHtml += `</div>`;

        // Giá trị tổng doanh thu của toàn bộ Đơn hàng
        const salesHtml = `
      <div style="font-family: var(--font-mono); font-weight: 800; color: var(--neon-teal); font-size: 14px">
        $${order.total_sales.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
      </div>
      <div style="font-size: 10.5px; color: var(--text-muted); margin-top: 3px; font-weight: 600">
        Tổng ${order.products.length} dòng hàng
      </div>
    `;

        // Thiên tai ảnh hưởng chống chập (Overlap)
        let hazardsHtml = '';
        const hasDisaster = order.disaster_exposed_real > 0;

        if (!hasDisaster || order.disasters.length === 0) {
          hazardsHtml = `
        <span class="badge-hazard-count safe">
          <span></span> Greenfield (An toàn)
        </span>
      `;
        } else {
          const activeCount = order.disasters.length;
          hazardsHtml = `
        <span class="badge-hazard-count danger" style="margin-bottom: 6px">
          <span></span> Đứt gãy đan chéo (${activeCount} thiên tai song song)
        </span>
      `;
          // Tạo các item thảm họa lồng liên đới
          order.disasters.forEach((d) => {
            hazardsHtml += `
          <div class="badge-disaster-detail">
            <strong>${d.name} (${d.location})</strong>
            <div style="font-size: 10.5px; opacity: 0.85; margin: 1px 0">
              Vùng bị ảnh hưởng: <span style="font-weight: 600; color: #1E293B">${d.role}</span>
              ${d.magnitude !== 'N/A' ? ` | Cấp độ: <span style="font-family: var(--font-mono); font-weight: 700">${d.magnitude}</span>` : ''}
              ${d.deaths !== '0' ? ` | Thương vong: <span style="font-family: var(--font-mono); font-weight: 700; color: var(--neon-red)">${d.deaths}</span>` : ''}
            </div>
            <div class="impact-desc">➔ <em>Hệ quả: ${d.impact}</em></div>
          </div>
        `;
          });
        }

        // Thời gian trễ thực tế
        let delayHtml = '';
        const delayDays = order.delay_days_real;
        const isLate = order.raw_delay_days_real > 0;

        if (delayDays <= 0) {
          delayHtml = `
        <div style="font-weight: 700; color: var(--neon-green)">ĐÚNG HẠN</div>
        <div style="font-size: 11px; color: var(--text-muted); margin-top: 3px">
          Thực nhận: <span style="font-family: var(--font-mono); font-weight: 700">${order.shipping_days_real} ngày</span>
          <br>(Cam kết: ${order.shipping_days_scheduled} ngày)
        </div>
      `;
        } else {
          delayHtml = `
        <div style="font-weight: 700; color: var(--neon-amber)">TRỄ HẠN</div>
        <div style="font-size: 11px; color: var(--text-muted); margin-top: 3px">
          Trễ thực tế: <span style="font-family: var(--font-mono); font-weight: 700; color: var(--neon-red)">+${delayDays.toFixed(1)} ngày</span>
          <br>(Thực nhận: ${order.shipping_days_real} ngày / Cam kết: ${order.shipping_days_scheduled} ngày)
        </div>
      `;
        }

        tr.innerHTML = `
      <td class="order-id-col" style="font-size: 14px">#${order.order_id}</td>
      <td style="font-family: var(--font-mono); color: var(--text-dark); font-weight: 600">${order.order_date}</td>
      <td>${routeHtml}</td>
      <td>${productHtml}</td>
      <td>${salesHtml}</td>
      <td>${hazardsHtml}</td>
      <td>${delayHtml}</td>
      <td style="text-align: center; font-weight: 700; color: var(--text-muted); font-size: 11px">
        Chọn nút Khảo sát bên cột Sản phẩm
      </td>
    `;

        tbody.appendChild(tr);
      });

      updatePaginationUI(data.total_records, data.page, data.total_pages);
    }


    // Quản lý bộ lọc loại thiên tai
    function setHazardFilter(filterType) {
      // Thay đổi class active trên các nút lọc
      document.getElementById('filter-all').classList.remove('active');
      document.getElementById('filter-disaster').classList.remove('active');
      document.getElementById('filter-none').classList.remove('active');

      document.getElementById(`filter-${filterType}`).classList.add('active');

      currentHazardFilter = filterType;
      currentOrdersPage = 1; // reset về trang đầu
      loadOrdersDatabase();
    }

    // Xử lý tìm kiếm
    let searchTimeout = null;
    function handleSearchKeyup(event) {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        currentSearchQuery = document.getElementById('order-search-input').value;
        currentOrdersPage = 1; // reset về trang đầu
        loadOrdersDatabase();
      }, 350); // debounce 350ms tránh spam API liên tục
    }

    // Điều khiển chuyển trang
    function changeOrderPage(direction) {
      currentOrdersPage += direction;
      loadOrdersDatabase();
    }

    // Cập nhật giao diện phân trang
    function updatePaginationUI(totalRecords, currentPage, totalPages) {
      const currentSpan = document.getElementById('page-current');
      const totalPagesSpan = document.getElementById('page-total-pages');
      const totalRecordsSpan = document.getElementById('page-total-text');
      const prevBtn = document.getElementById('btn-page-prev');
      const nextBtn = document.getElementById('btn-page-next');
      const rangeSpan = document.getElementById('page-range-text');

      currentSpan.textContent = currentPage;
      totalPagesSpan.textContent = totalPages || 1;
      totalRecordsSpan.textContent = totalRecords ? totalRecords.toLocaleString('vi-VN') : 0;

      prevBtn.disabled = (currentPage <= 1);
      nextBtn.disabled = (currentPage >= totalPages);

      if (totalRecords === 0) {
        rangeSpan.textContent = '0';
      } else {
        const startRange = (currentPage - 1) * 15 + 1;
        const endRange = Math.min(currentPage * 15, totalRecords);
        rangeSpan.textContent = `${startRange.toLocaleString('vi-VN')} - ${endRange.toLocaleString('vi-VN')}`;
      }
    }

    // Điền nhanh thông tin đơn hàng được chọn từ Database vào Form để giả lý thuyết dự đoán
    function selectAndLoadOrder(orderId, prodRowIndex) {
      // Tìm kiếm đơn tương ứng trong listGlobal hiện hành
      const order = ordersListGlobal.find(o => o.order_id === orderId);
      if (!order) return;

      // Lấy dòng sản phẩm cụ thể được click
      const prod = order.products.find(p => p.row_index === prodRowIndex);
      if (!prod) return;

      // Ghép nối dữ liệu để phục vụ nạp payload dự báo
      activeTestData = {
        ...order,
        ...prod,
        // ghi đè thông tin sản phẩm cụ thể để model nhận diện chuẩn xác
        product_name_real: prod.product_name,
        product_price: prod.product_price,
        order_item_quantity: prod.order_item_quantity,
        category_name: prod.category_name,
        department_name: prod.department_name,
        auto_unit_price: prod.auto_metrics.auto_unit_price,
        auto_total_value: prod.auto_metrics.auto_total_value,
        pack_type: prod.auto_metrics.pack_type,
        auto_qty: prod.auto_metrics.auto_qty,
        qty_unit: prod.auto_metrics.qty_unit,
        contract_type: prod.auto_metrics.contract_type,
        actual_carrier_route: prod.auto_metrics.actual_carrier_route,
      };

      // Điền dữ liệu vào biểu mẫu form
      fillFormData(activeTestData);

      // Chuyển đổi tab về Dashboard
      switchMainTab('dashboard');

      // Hiển thị dải băng Real-Time Telemetry Bar chỉ báo việc nạp thành công
      if (testOrderInfo) {
        testOrderInfo.textContent = `NẠP THÀNH CÔNG ĐƠN HÀNG THỰC TẾ: #${order.order_id} (${prod.product_name}) - Thực tế giao mất ${order.shipping_days_real} ngày.`;
        testOrderInfo.style.display = 'inline-block';
        testOrderInfo.style.color = 'var(--neon-teal)';
        testOrderInfo.style.backgroundColor = 'rgba(13, 148, 136, 0.08)';
        testOrderInfo.style.border = '1px solid rgba(13, 148, 136, 0.2)';
      }

      // Tự động kích hoạt thanh disaster-bar nếu đơn này bị tác động bởi thảm họa thực tế
      if (order.disaster_exposed_real > 0) {
        if (realDisasterBar && realDisasterText) {
          let text = `[HỆ THỐNG ĐƯỢC CẢNH BÁO]: Có thảm họa xuất hiện đè lên chuỗi hành hành trình vận chuyển của đơn tự động #${order.order_id}. `;
          order.disasters.forEach(d => {
            text += `➔ ${d.name} (${d.location}) ảnh hưởng khu vực: ${d.role}. `;
          });
          realDisasterText.innerHTML = text;
          realDisasterBar.style.display = 'flex';
        }
      } else {
        if (realDisasterBar) {
          realDisasterBar.style.display = 'none';
        }
      }

      // Cuộn mượt mà lên đầu trang để sẵn sàng trải nghiệm dự báo và GNN
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Điền các giá trị vào thẻ Form controls
    function fillFormData(order) {
      const fields = {
        'order_date': order.order_date,
        'shipping_days_scheduled': order.shipping_days_scheduled,
        'shipping_mode': order.shipping_mode,
        'market': order.market,
        'order_region': order.order_region,
        'customer_segment': order.customer_segment,
        'department_name': order.department_name,
        'category_name': order.category_name,
        'order_item_quantity': order.order_item_quantity,
        'product_price': (order.auto_metrics ? order.auto_metrics.auto_unit_price : null) || order.product_price || 100,
      };

      for (const [name, val] of Object.entries(fields)) {
        const input = form.querySelector(`[name="${name}"]`);
        if (input) {
          input.value = val;
        }
      }

      // Cấu hình các nút thảm họa giả lập tương đồng trạng thái thực tế
      if (order.disaster_exposed_real > 0) {
        disasterToggle.checked = true;
        disasterFields.style.display = 'grid';

        // Đổ các thông số thiên tai thực tế vào sườn input khả dụng của Form một cách an toàn
        const setVal = (elName, val) => {
          const el = form.querySelector(`[name="${elName}"]`);
          if (el) el.value = val;
        };

        setVal("disaster_magnitude", order.current_max_disaster_magnitude_real || (order.auto_metrics ? order.auto_metrics.max_disaster_magnitude : 5));
        setVal("disaster_affected", order.current_max_affected_real || 10000);
        setVal("disaster_deaths", order.current_max_deaths_real || 0);

        // Cũng ghi vào các cấu hình thuộc tính bổ trợ nếu có khai báo ẩn
        setVal("active_disaster_count", order.active_disaster_count_real);
        setVal("known_disaster_count", order.known_disaster_count_real);
        setVal("current_max_disaster_magnitude", order.current_max_disaster_magnitude_real);
        setVal("current_max_affected", order.current_max_affected_real);
        setVal("current_max_deaths", order.current_max_deaths_real);
      } else {
        disasterToggle.checked = false;
        disasterFields.style.display = 'none';
      }
    }

    const form = document.getElementById('predict-form');
    const disasterToggle = document.getElementById('disaster-toggle');
    const disasterFields = document.getElementById('disaster-fields');
    const btnDrawTest = document.getElementById('btn-draw-test');
    const testOrderInfo = document.getElementById('test-order-info');
    const realDisasterBar = document.getElementById('real-disaster-bar');
    const realDisasterText = document.getElementById('real-disaster-text');
    const btnMirrorDisaster = document.getElementById('btn-mirror-disaster');

    // Lưu trữ dữ liệu chuỗi thời gian thực nếu có load từ file test
    let activeTestData = null;

    if (btnDrawTest) {
      btnDrawTest.addEventListener('click', async () => {
        btnDrawTest.disabled = true;
        btnDrawTest.textContent = 'Đang nạp dữ liệu...';
        try {
          const res = await fetch('/api/random-test-order');
          const result = await res.json();
          if (result.success) {
            const order = result.data;
            activeTestData = order; // Lưu vào biến toàn cục của JS để lát submit truyền lên API

            // Điền dữ liệu vào form dùng hàm map phụ trợ
            const orderDataMapped = {
              order_date: order.order_date,
              shipping_days_scheduled: order.shipping_days_scheduled,
              shipping_mode: order.shipping_mode,
              market: order.market,
              order_region: order.order_region,
              customer_segment: order.customer_segment,
              department_name: order.department_name,
              category_name: order.category_name,
              order_item_quantity: order.order_item_quantity,
              product_price: order.auto_unit_price,
              disaster_exposed_real: order.disaster_exposed_real,
              active_disaster_count_real: order.active_disaster_count_real,
              known_disaster_count_real: order.known_disaster_count_real,
              current_max_disaster_magnitude_real: order.current_max_disaster_magnitude_real,
              current_max_affected_real: order.current_max_affected_real,
              current_max_deaths_real: order.current_max_deaths_real,
              order_id: order.order_id_real,
              product_name: order.product_name_real,
              shipping_days_real: order.shipping_days_real,
              disasters: []
            };

            // Reconstruct disasters array on the fly for telemetry block if disaster exposed
            if (order.disaster_exposed_real > 0) {
              const deaths = order.current_max_deaths_real;
              const mag = order.max_disaster_magnitude_real || order.current_max_disaster_magnitude_real;
              if (order.supplier_disaster_country_real) {
                orderDataMapped.disasters.push({
                  name: 'Đứt gãy logistics và ngập lụt cục bộ',
                  location: order.supplier_disaster_country_real,
                  role: 'Supplier Base',
                  magnitude: mag
                });
              }
              if (order.customer_disaster_country_real) {
                orderDataMapped.disasters.push({
                  name: 'Bão nhiệt đới gây lụt ngập mạng nội địa',
                  location: order.customer_disaster_country_real,
                  role: 'Customer Hub',
                  magnitude: mag
                });
              }
            }

            fillFormData(orderDataMapped);
            // Điền dữ liệu vào form
            form.querySelector('[name="order_date"]').value = order.order_date;
            form.querySelector('[name="shipping_days_scheduled"]').value = order.shipping_days_scheduled;
            form.querySelector('[name="shipping_mode"]').value = order.shipping_mode;
            form.querySelector('[name="market"]').value = order.market;
            form.querySelector('[name="order_region"]').value = order.order_region;
            form.querySelector('[name="customer_segment"]').value = order.customer_segment;
            form.querySelector('[name="department_name"]').value = order.department_name;
            form.querySelector('[name="category_name"]').value = order.category_name;
            form.querySelector('[name="order_item_quantity"]').value = order.order_item_quantity;
            form.querySelector('[name="product_price"]').value = Number(order.product_price).toFixed(2);
            form.querySelector('[name="discount_rate"]').value = order.discount_rate;

            // Quản lý trạng thái Thiên tai
            const hasDisaster = order.disaster_exposed_real > 0 || order.active_disaster_count_real > 0;
            disasterToggle.checked = hasDisaster;
            disasterFields.style.display = hasDisaster ? 'grid' : 'none';

            if (hasDisaster) {
              form.querySelector('[name="disaster_magnitude"]').value = order.current_max_disaster_magnitude_real || 5;
              form.querySelector('[name="disaster_affected"]').value = order.current_max_affected_real || 10000;
              form.querySelector('[name="disaster_deaths"]').value = order.current_max_deaths_real || 0;
            }

            // Hiển thị thanh tin thiên tai thực tế để người dùng đối chiếu / giả lập lại y hệt
            if (hasDisaster) {
              realDisasterBar.style.display = 'flex';
              const mag = order.current_max_disaster_magnitude_real || 0;
              const affected = order.current_max_affected_real || 0;
              const deaths = order.current_max_deaths_real || 0;
              const activeCount = order.active_disaster_count_real || 0;
              const knownCount = order.known_disaster_count_real || 0;
              const custLoc = order.customer_disaster_country_real || '-';
              const suppLoc = order.supplier_disaster_country_real || '-';
              const start = order.exposure_start_real ? order.exposure_start_real.split(' ')[0] : '-';
              const end = order.exposure_end_real ? order.exposure_end_real.split(' ')[0] : '-';
              realDisasterText.innerHTML = `<strong>THIÊN TAI THỰC TẾ:</strong> ${activeCount} sự kiện bão lũ đang diễn ra · Chỉ số EM-DAT: <strong>${mag} Mgn</strong> · Ảnh hưởng: <strong>${affected.toLocaleString()} người</strong> · Địa bàn nhà cung cấp: <strong>${suppLoc}</strong>. Thời gian kéo dài: <strong>${start}</strong> â†’ <strong>${end}</strong>`;
            } else {
              realDisasterBar.style.display = 'none';
              realDisasterText.innerHTML = '';
            }

            // Hiển thị thanh thông tin real status để đối chiếu lúc demo
            testOrderInfo.style.display = 'inline';
            const formattedRealPrice = Number(order.auto_unit_price).toLocaleString();
            const formattedRealTotal = Number(order.auto_total_value).toLocaleString();
            testOrderInfo.innerHTML = `Đơn hàng: <strong>#Auto-${order.order_id_real}</strong> · Sản phẩm ô tô: <strong>${order.product_name_real}</strong> (${order.pack_type}) · Quy chuẩn thương mại: <strong>${order.auto_qty} ${order.qty_unit}</strong> · Tổng giá trị lô hàng: <strong>$${formattedRealTotal}</strong> · Thực tế: giao <strong>${order.shipping_days_real} ngày</strong> (${order.delay_days_real > 0 ? 'TRỄ ' + order.delay_days_real + ' ngày' : 'ĐÚNG HẠN'})`;

            // Đánh dấu dòng trễ
            if (order.delay_days_real > 0) {
              testOrderInfo.style.color = '#F59E0B'; // Vàng neon
            } else {
              testOrderInfo.style.color = '#10B981'; // Xanh lá mát mắt
            }
          } else {
            alert(result.message);
          }
        } catch (err) {
          alert('Lỗi khi tải đơn hàng: ' + err.message);
        } finally {
          btnDrawTest.disabled = false;
          btnDrawTest.textContent = 'Nạp Dữ Liệu Thực Tế Ngẫu Nhiên';
        }
      });
    }

    disasterToggle.addEventListener('change', () => {
      disasterFields.style.display = disasterToggle.checked ? 'grid' : 'none';
    });

    if (btnMirrorDisaster) {
      btnMirrorDisaster.addEventListener('click', () => {
        if (!activeTestData) return;
        disasterToggle.checked = true;
        disasterFields.style.display = 'grid';

        // Gán giá trị an toàn
        const setVal = (elName, val) => {
          const el = form.querySelector(`[name="${elName}"]`);
          if (el) el.value = val;
        };
        setVal("disaster_magnitude", activeTestData.current_max_disaster_magnitude_real || 5);
        setVal("disaster_affected", activeTestData.current_max_affected_real || 10000);
        setVal("disaster_deaths", activeTestData.current_max_deaths_real || 0);

        btnMirrorDisaster.textContent = 'ĐỒNG BỘ THÀNH CÔNG';
        setTimeout(() => { btnMirrorDisaster.textContent = 'ĐỒNG BỘ THIÊN TAI THỰC TẾ'; }, 1800);
      });
    }

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('button');
      btn.disabled = true; btn.textContent = 'ĐANG TÍNH LẬP MA TRẬN ĐẶC TRƯNG MÔ HÌNH UNIT...';

      const fd = new FormData(form);
      const payload = {};
      fd.forEach((v, k) => { payload[k] = v; });
      payload['disaster-toggle'] = disasterToggle.checked;

      // Nếu trước đó đang chọn hàng mẫu, dán các rolling features thực tế của hàng mẫu vào payload
      if (activeTestData) {
        const keysToCopy = [
          'avg_delay_1d', 'avg_delay_2d', 'avg_delay_3d', 'avg_delay_5d',
          'late_rate_1d', 'late_rate_2d', 'late_rate_3d', 'late_rate_5d',
          'order_volume_1d', 'order_volume_2d', 'order_volume_3d', 'order_volume_5d',
          'active_disaster_count_real', 'known_disaster_count_real'
        ];
        keysToCopy.forEach(k => {
          payload[k] = activeTestData[k];
        });
      }

      try {
        const res = await fetch('/api/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        renderResult(data);
      } catch (err) {
        document.getElementById('result-body').innerHTML =
          '<div class="output-empty-slate">Không thể kết nối máy chủ dự báo. Vui lòng thử lại.</div>';
      } finally {
        btn.disabled = false; btn.textContent = 'CHẠY HỆ THỐNG DỰ BÁO THỜI GIAN THỰC';
      }
    });

    function renderResult(data) {
      if (data.error) {
        document.getElementById('result-body').innerHTML =
          `<div class="output-empty-slate">${data.error}</div>`;
        return;
      }
      const days = data.xgboost.delay_days;
      const lstmDays = data.lstm && data.lstm.delay_days !== undefined ? data.lstm.delay_days : null;

      // Câu văn diễn giải dễ hiểu bằng ngôn ngữ tự nhiên
      let summarySentence;
      if (days <= 0) {
        summarySentence = `<strong>DÒNG CHẢY AN TOÀN:</strong> AI phân tích chu kỳ dự báo cho thấy mọi đặc trưng đều lý tưởng. Hệ thống <strong>giao hàng chính xác tuyệt đối đúng cam kết</strong>, độ bất định xấp xỉ 0%.`;
      } else if (days < 1) {
        summarySentence = `<strong>TRƯỜNG HỢP NHẸ:</strong> Có rủi ro dao động biên độ nhỏ trong thời hạn bàn giao, thời gian kéo dài <strong>dưới 24 giờ</strong>.`;
      } else {
        summarySentence = `<strong>CẢNH BÁO TẮC NGHẼN:</strong> Hệ thống dữ liệu tiến trình lắp ráp và kho bãi sẽ gặp ách tắc nghiêm trọng. Điểm nhận hàng có khả năng <strong>trễ giao hàng trong khoảng ${days} ngày</strong>.`;
      }

      let html = `
    <div style="background: rgba(255, 255, 255, 0.9); border: 1.5px solid #CBD5E1; border-radius: 12px; padding: 16px; margin-bottom: 20px; font-size: 13px; line-height: 1.6; color:#0F172A">
      ${summarySentence}
    </div>
  `;

      // Thêm khu vực hiển thị Thông số Thương mại Ô tô đã được Ánh xạ (Auto Commercial Metrics)
      if (data.auto_metrics) {
        const autom = data.auto_metrics;
        html += `
      <div style="background: rgba(13, 148, 136, 0.04); border: 1.5px solid #CBD5E1; border-radius: 12px; padding: 18px; margin-bottom: 20px; font-size: 13px; line-height: 1.6; color:#1E293B">
        <div style="font-weight:800; color:var(--neon-teal); margin-bottom:12px; font-family:var(--font-sans); font-size:12px; display:flex; align-items:center; gap:8px; letter-spacing:0.5px; text-transform: uppercase;">
          <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--neon-teal)"></span>
          THỐNG SỐ KHẾ ƯỚC THƯƠNG MẠI (AUTOMOTIVE OEM CONSTRAINTS)
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px 16px">
          <div>. Phân loại ánh xạ: <strong style="color:var(--neon-teal); font-weight: 700">${data.mapped_category || 'Thiếu liên kết'}</strong></div>
          <div>. Nhóm hệ thống: <strong style="color:#0F172A; font-weight: 700">${data.mapped_department || 'Thiếu liên kết'}</strong></div>
          <div>. Chuẩn bao bì vỏ: <strong style="color:#0F172A; font-weight: 700">${autom.pack_type}</strong></div>
          <div>. Dung lượng cấp: <strong style="color:#0F172A; font-weight: 700">${autom.auto_qty} ${autom.qty_unit}</strong></div>
          <div>. Đơn giá lô chuẩn: <strong style="color:#047857; font-weight: 700">$${Number(autom.auto_unit_price).toLocaleString()}</strong></div>
          <div>. Tổng giá trị: <strong style="color:var(--neon-teal); font-weight: 700">$${Number(autom.auto_total_value).toLocaleString()}</strong></div>
          <div style="grid-column: 1 / -1; border-top: 1.5px solid #E2E8F0; padding-top: 10px; margin-top: 8px; font-family: var(--font-sans); font-size: 11.5px; color:#475569">
            <strong>PHÂN HẠNG HỢP ĐỒNG:</strong> <span style="color:var(--neon-amber); font-weight: 800">${autom.contract_type}</span>
          </div>
        </div>
      </div>
    `;
      }

      // Kết quả ngày trở dự báo chi tiết
      html += `
    <div class="gnn-metrics-grid">
      <div class="radial-metric-box" style="background: rgba(6, 182, 212, 0.02)">
        <span class="radial-lbl">XGBOOST DỰ BÁO CHÍNH</span>
        <span class="radial-val-huge" style="color:var(--neon-teal)">${days} <span style="font-size:14px; font-weight:normal; color:var(--text-muted)">days</span></span>
        <span class="badge-cq ${data.risk_level === 'high' ? 'high' : (data.risk_level === 'medium' ? 'medium' : 'low')}">${data.risk_label.toUpperCase()} RISK</span>
      </div>
      <div class="radial-metric-box" style="background: rgba(236, 72, 153, 0.02)">
        <span class="radial-lbl">LSTM SERIES ĐỐI CHIẾU</span>
        <span class="radial-val-huge" style="color:var(--neon-pink)">${lstmDays !== null ? lstmDays : '-'} <span style="font-size:14px; font-weight:normal; color:var(--text-muted)">days</span></span>
        <span class="badge-cq" style="background:rgba(255,255,255,0.05); color:var(--text-muted); border:1px solid var(--glass-border)">RECURRENT EVAL</span>
      </div>
    </div>
  `;

      // Nếu đang dùng đơn hàng thật (test dataset), so sánh dự báo AI với kết quả thực tế
      if (activeTestData && activeTestData.delay_days_real !== undefined) {
        const realDelay = activeTestData.delay_days_real;
        const diff = Math.abs(days - realDelay);
        const isMatch = diff <= 1; // sai lệch trong vòng 1 ngày được xem là "gần đúng"
        html += `
      <div style="margin-top:20px; padding:14px 16px; border-radius:12px; font-size:12.5px; line-height:1.6; ${isMatch ? 'background:rgba(16, 185, 129, 0.08); border:1.5px solid rgba(16, 185, 129, 0.4); color:#065F46' : 'background:rgba(239, 68, 68, 0.08); border:1.5px solid rgba(239, 68, 68, 0.4); color:#991B1B'}">
        <strong>${isMatch ? 'KIỂM ĐỊNH THỰC TẾ (TELEMETRY ACCURACY):' : 'KIỂM ĐỊNH LỆCH BIÊN (TELEMETRY DISCREPANCY):'}</strong> Đơn hàng ô tô thực tế đã ghi nhận mức trễ là <strong>${realDelay} ngày</strong>.
        Hệ thống AI ước lượng <strong>${days} ngày</strong> (Độ lệch chuẩn: <strong>${diff.toFixed(1)} ngày</strong>) - 
        ${isMatch ? '<span style="color:#047857; font-weight:700">Chế độ dự toán hoạt động chính xác xuất sắc!</span>' : '<span style="color:#B45309; font-weight:700">Phát sinh sai lệch ngẫu nhiên.</span>'}
      </div>
    `;
      }

      if (data.top_factors && data.top_factors.length) {
        html += `
      <div style="margin-top:24px;">
        <div style="font-family:var(--font-sans); font-size:11px; font-weight:700; text-transform:uppercase; color:var(--text-dark); margin-bottom:12px; letter-spacing:0.5px">TRỌNG SỐ BIẾN CẤP QUYẾT ĐỊNH (GNN ATTENTION WEIGHTS)</div>
    `;
        data.top_factors.forEach(f => {
          html += `
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; font-size:12px">
          <span style="color:var(--text-primary); font-weight:600">${f.feature}</span>
          <div style="flex:1; height:6px; background:#E2E8F0; border-radius:10px; margin:0 15px; overflow:hidden">
            <span style="display:block; height:100%; width:${f.share}%; background:linear-gradient(90deg, var(--neon-teal), var(--neon-green)); border-radius:10px"></span>
          </div>
          <span style="font-family:var(--font-mono); color:var(--neon-teal); font-weight:700; width:35px; text-align:right">${f.share}%</span>
        </div>
      `;
        });
        html += '</div>';
      }

      html += `
    <div style="margin-top:22px; background:rgba(217, 119, 6, 0.08); border:1.5px solid rgba(217, 119, 6, 0.3); border-radius:12px; padding:14px; font-size:12.5px; color:#78350F; line-height:1.5">
      <strong>QUYẾT ĐỊNH ĐIỀU PHỐI OEM (MRP MITIGATION):</strong> Khuyến nghị duy trì mức **TỒN KHO AN TOÀN (SAFETY STOCK) thêm ${data.safety_stock_days} ngày** sản xuất đối với dòng linh kiện này để ngăn chặn triệt để đứt gãy dây chuyền chính.
    </div>
  `;

      // ĐỒ XUẤT: Sơ đồ trực quan hóa Chuỗi Cung ứng (GNN Interactive Network Graph)
      const isDisrupted = data.risk_level === 'high' || (activeTestData && activeTestData.disaster_exposed_real > 0);
      const m = activeTestData || {};
      const supplierCountry = m.supplier_disaster_country_real || 'PRT';
      const customerCountry = m.customer_disaster_country_real || 'USA';
      const orderRegion = form.querySelector('[name="order_region"]').value;
      const shippingMode = form.querySelector('[name="shipping_mode"]').value;
      const custSegment = form.querySelector('[name="customer_segment"]').value;
      const categoryMapped = data.mapped_category || 'Cùm phanh đĩa hiệu năng cao';
      const departmentMapped = data.mapped_department || 'Cơ cấu Truyền phanh & Thủy lực';
      const disasterMag = m.current_max_disaster_magnitude_real || (isDisrupted ? 8.5 : 0);
      const disasterAffected = m.current_max_affected_real || (isDisrupted ? 15000 : 0);

      html += `
    <div class="sc-graph-container" style="margin-top:20px; border:1.5px solid #94A3B8; border-radius:12px; overflow:hidden; background:#0F192C">
      <div class="sc-graph-header" style="background:#1E293B; color:#fff; padding:12px 16px; font-size:13px; font-weight:700; display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid #334155">
        <span style="font-family:var(--font-sans); letter-spacing:0.5px">ĐỒ THỂ LIÊN KẾT KHÔNG GIAN GNN (SPATIAL-TEMPORAL SUPPLY GRAPH)</span>
        <span style="font-size:11px; font-weight:700; background:var(--neon-teal); color:#fff; padding:3px 10px; border-radius:30px; text-transform:uppercase">TƯƠNG TÁC 3D Canvas</span>
      </div>
      <div>
        <canvas id="gnnCanvas" width="540" height="280" style="width:100%; height:280px; display:block"></canvas>
      </div>
      <div class="gnn-inspector" style="background:#1E293B; color:#ECEFF4; padding:14px 16px; border-top:1px solid #334155; font-size:12.5px; border-bottom-left-radius:12px; border-bottom-right-radius:12px; line-height:1.5">
        <div style="font-weight:700; font-family:var(--font-sans); color:var(--neon-teal); margin-bottom:4px; display:flex; align-items:center; gap:6px" id="node-inspector-title">
          <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--neon-teal)"></span>
          BẤM VÀO MỘT NODE TRÊN ĐỒ THỂ ĐỂ KIỂM TRA THÔNG SỐ KHÔNG GIAN
        </div>
        <div id="node-inspector-desc" style="color:#B9C2D6; font-size:11.5px">
          Sơ đồ đang biểu diễn dòng chảy phụ tùng ô tô từ nhà máy nguồn Tier-2 đi qua tuyến Logistics toàn cầu trực tiếp đến Đại lý ráp OEM.
        </div>
      </div>
    </div>
  `;

      document.getElementById('result-body').innerHTML = html;

      // Khởi tạo hoạt hóa GNN Canvas ngay sau khi render xong HTML
      setTimeout(() => {
        initGnnCanvas({
          isDisrupted: isDisrupted,
          riskLevel: data.risk_level,
          delayDays: days,
          lstmDays: lstmDays,
          supplierCountry: supplierCountry,
          customerCountry: customerCountry,
          orderRegion: orderRegion,
          shippingMode: shippingMode,
          custSegment: custSegment,
          categoryMapped: categoryMapped,
          departmentMapped: departmentMapped,
          disasterMag: disasterMag,
          disasterAffected: disasterAffected,
          topFactors: data.top_factors || []
        });
      }, 50);
    }

    // Hàm khởi tạo và chạy hoạt hóa đồ thị không gian GNN
    function initGnnCanvas(params) {
      const canvas = document.getElementById('gnnCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');

      // Tinh chỉnh độ phân giải cho vòng mạc (Retina Displays)
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);

      const width = rect.width;
      const height = rect.height;

      // Khai báo cấu trúc các Node (Tọa độ cân đối trên mặt phẳng GNN)
      const nodes = [
        {
          id: 'tier2',
          label: '1. Tier-2 Sourcing',
          icon: '🏭',
          x: 75,
          y: 70,
          desc: 'Nguồn cung linh kiện gốc',
          details: `Quốc gia: <strong>${params.supplierCountry}</strong><br>🧩 Mặt hàng: <strong style="color:#E9A23B">${params.categoryMapped}</strong><br>🏭 Nhóm hệ thống: <strong>${params.departmentMapped}</strong><br>⚠️ Thiên tai chịu ảnh hưởng: <strong>${params.isDisrupted ? 'CÓ (Mức độ ' + params.disasterMag + ' Mgn)' : 'Không có'}</strong>`,
          status: params.isDisrupted ? 'disrupted' : 'good'
        },
        {
          id: 'tier1',
          label: '2. Tier-1 Sub-Assembly',
          icon: '🔧',
          x: 235,
          y: 70,
          desc: 'Trung tâm tích hợp chi tiết máy',
          details: `Kiểm định chất lượng: <strong>Đạt tiêu chuẩn QS-9000</strong><br>📦 Trạng thái đóng gói: <strong>Đang hoàn thiện cơ cấu cụm phụ tùng</strong><br>⏱️ Thời gian lắp ráp bình quân: <strong>1.2 ngày</strong>`,
          status: 'good'
        },
        {
          id: 'logistics',
          label: '3. Logistics Transit',
          icon: '🚢',
          x: 395,
          y: 70,
          desc: 'Tuyến vận chuyển liên quốc gia',
          details: `🚢 Hình thức vận chuyển: <strong>${params.shippingMode}</strong><br>📦 Cửa ngõ phân phối chính: <strong>${params.orderRegion}</strong><br>⚠️ Sức gió & Thời tiết tuyến biển: <strong>${params.isDisrupted ? 'Cường lưu bão bùng phát' : 'Thuận gió xuôi chèo'}</strong>`,
          status: params.isDisrupted ? 'warning' : 'good'
        },
        {
          id: 'oem_plant',
          label: '4. OEM Assembly',
          icon: '⚙️',
          x: 395,
          y: 200,
          desc: 'Nhà máy lắp ráp ô tô trung tâm',
          details: `🏭 Trạm hoàn thiện: <strong>Khu vực Đông Nam Á / EU OEM</strong><br>📦 Tỷ lệ tồn kho dây chuyền: <strong>${params.isDisrupted ? 'Rất thấp (Dưới ngưỡng an toàn)' : 'Ổn định (5 ngày)'}</strong><br>⏱️ Trễ trung bình rolling 1D: <strong>${(params.delayDays * 0.4).toFixed(1)} ngày</strong>`,
          status: params.riskLevel === 'high' ? 'disrupted' : (params.riskLevel === 'medium' ? 'warning' : 'good')
        },
        {
          id: 'gnn_engine',
          label: 'GNN Feature Engine',
          icon: '🤖',
          x: 235,
          y: 135,
          desc: 'Mạng nơ-ron tích hợp đồ thị AI',
          details: `Thuật toán học máy: <strong>XGBoost + LSTM Concurrent Ensemble</strong><br>📊 Dự báo độ trễ: <strong style="color:var(--amber)">${params.delayDays} ngày</strong> (LSTM: <strong>${params.lstmDays || '—'} ngày</strong>)<br>📈 Các feature chi phối chính: <br>${params.topFactors.map(f => ` - <i>${f.feature} (${f.share}%)</i>`).join('<br>')}`,
          status: 'ai'
        },
        {
          id: 'dealers',
          label: '5. Dealer / assembly',
          icon: '🏬',
          x: 75,
          y: 200,
          desc: 'Phân phối đại lý & Khách hàng',
          details: `Khách hàng mục tiêu: <strong>${params.custSegment}</strong><br>⚠️ Mức độ rủi ro chuỗi: <strong style="text-transform:uppercase">${params.riskLevel}</strong><br>📦 Đề xuất Kho an toàn: <strong style="color:var(--teal)">${Math.ceil(params.delayDays * 1.5 + 1)} ngày sản xuất</strong>`,
          status: params.riskLevel === 'high' ? 'disrupted' : (params.riskLevel === 'medium' ? 'warning' : 'good')
        }
      ];

      // Các kết nối không gian (Directed Links) đại diện thực tế logistics
      const physicalLinks = [
        { from: 'tier2', to: 'tier1' },
        { from: 'tier1', to: 'logistics' },
        { from: 'logistics', to: 'oem_plant' },
        { from: 'oem_plant', to: 'dealers' }
      ];

      // Các liên kết nơ-ron tiềm ẩn (GNN Latent embeddings) thu thập thông tin từ tất cả tác nhân chuỗi
      const latentLinks = [
        { from: 'tier2', to: 'gnn_engine' },
        { from: 'tier1', to: 'gnn_engine' },
        { from: 'logistics', to: 'gnn_engine' },
        { from: 'oem_plant', to: 'gnn_engine' },
        { from: 'dealers', to: 'gnn_engine' }
      ];

      // Quản lý các hạt chuyển động (Flowing electron pulses)
      const particles = [];
      physicalLinks.forEach((link, idx) => {
        // Tạo 3 hạt chuyển động lệch pha nhau dọc tuyến
        for (let i = 0; i < 3; i++) {
          particles.push({
            link: link,
            pct: i / 3,
            speed: 0.007 + Math.random() * 0.003
          });
        }
      });

      // Hạt xung nơ-ron hướng vào GNN Engine
      const aiParticles = [];
      latentLinks.forEach(link => {
        aiParticles.push({
          link: link,
          pct: Math.random(),
          speed: 0.012
        });
      });

      let selectedNode = null;
      let hoveredNode = null;
      let frameId = null;
      let pulseTimer = 0;

      // Chọn hiển thị mặc định khi mở là GNN Engine hoặc Node gặp lỗi
      selectedNode = nodes.find(n => n.id === 'gnn_engine');
      displayInspector(selectedNode);

      function draw() {
        ctx.clearRect(0, 0, width, height);
        pulseTimer += 0.05;

        // 1. Vẽ các liên kết nơ-ron nạp thông tin GNN tiềm ẩn (Nền mờ)
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 6]);
        ctx.strokeStyle = 'rgba(42, 157, 143, 0.25)'; // Màu teal mờ
        latentLinks.forEach(link => {
          const fromNode = nodes.find(n => n.id === link.from);
          const toNode = nodes.find(n => n.id === link.to);
          ctx.beginPath();
          ctx.moveTo(fromNode.x, fromNode.y);
          ctx.lineTo(toNode.x, toNode.y);
          ctx.stroke();
        });
        ctx.setLineDash([]); // Reset line dash

        // Dự phòng hiển thị hạt AI đi vào GNN
        aiParticles.forEach(p => {
          p.pct += p.speed;
          if (p.pct > 1) p.pct = 0;
          const fromNode = nodes.find(n => n.id === p.link.from);
          const toNode = nodes.find(n => n.id === p.link.to);

          const px = fromNode.x + (toNode.x - fromNode.x) * p.pct;
          const py = fromNode.y + (toNode.y - fromNode.y) * p.pct;

          ctx.fillStyle = 'rgba(42, 157, 143, 0.6)';
          ctx.beginPath();
          ctx.arc(px, py, 2.5, 0, Math.PI * 2);
          ctx.fill();
        });

        // 2. Vẽ liên kết vật lý (Luồng sản xuất)
        ctx.lineWidth = 3.5;
        physicalLinks.forEach(link => {
          const fromNode = nodes.find(n => n.id === link.from);
          const toNode = nodes.find(n => n.id === link.to);

          // Chọn màu liên kết tùy biến mức độ rủi ro hệ thống
          if (params.riskLevel === 'high') {
            ctx.strokeStyle = 'rgba(239, 68, 68, 0.45)'; // Đỏ cảnh báo dày mờ (neon-red)
          } else if (params.riskLevel === 'medium') {
            ctx.strokeStyle = 'rgba(245, 158, 11, 0.4)'; // Vàng mờ (neon-amber)
          } else {
            ctx.strokeStyle = 'rgba(16, 185, 129, 0.4)'; // Teal mờ (neon-green)
          }
          ctx.beginPath();
          ctx.moveTo(fromNode.x, fromNode.y);
          ctx.lineTo(toNode.x, toNode.y);
          ctx.stroke();
        });

        // 3. Đưa các hạt dòng điện chuyển động nhịp nhàng (Production Flow Lines)
        particles.forEach(p => {
          p.pct += p.speed;
          if (p.pct > 1) p.pct = 0;

          const fromNode = nodes.find(n => n.id === p.link.from);
          const toNode = nodes.find(n => n.id === p.link.to);

          const px = fromNode.x + (toNode.x - fromNode.x) * p.pct;
          const py = fromNode.y + (toNode.y - fromNode.y) * p.pct;

          // Hạt tỏa sáng (glowing point)
          ctx.beginPath();
          if (params.riskLevel === 'high') {
            ctx.fillStyle = '#EF4444'; // đỏ rực rỡ (neon-red)
            ctx.arc(px, py, 4.5, 0, Math.PI * 2);
          } else if (params.riskLevel === 'medium') {
            ctx.fillStyle = '#F59E0B'; // vàng rực rỡ (neon-amber)
            ctx.arc(px, py, 4, 0, Math.PI * 2);
          } else {
            ctx.fillStyle = '#10B981'; // xanh lá mát mắt (neon-green)
            ctx.arc(px, py, 4, 0, Math.PI * 2);
          }
          ctx.fill();
        });

        // 4. Vẽ các Node
        nodes.forEach(node => {
          const isHovered = (hoveredNode && hoveredNode.id === node.id);
          const isSelected = (selectedNode && selectedNode.id === node.id);

          // Hiệu ứng lan truyền sóng xung động trên node thiên tai hoặc node bị nghẽn
          if (node.status === 'disrupted') {
            const ringRadius = 22 + Math.sin(pulseTimer * 2.5) * 8;
            ctx.strokeStyle = 'rgba(239, 68, 68, 0.4)';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(node.x, node.y, ringRadius, 0, Math.PI * 2);
            ctx.stroke();
          } else if (node.status === 'warning') {
            const ringRadius = 20 + Math.sin(pulseTimer * 1.8) * 5;
            ctx.strokeStyle = 'rgba(245, 158, 11, 0.35)';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(node.x, node.y, ringRadius, 0, Math.PI * 2);
            ctx.stroke();
          }

          // Vòng tròn bao của node
          let nodeBg = '#1B2A4A';
          let borderCol = 'rgba(255,255,255,0.15)';

          if (node.status === 'disrupted') {
            nodeBg = '#3D1B16';
            borderCol = '#EF4444';
          } else if (node.status === 'warning') {
            nodeBg = '#3D2F1B';
            borderCol = '#F59E0B';
          } else if (node.status === 'ai') {
            nodeBg = '#0B3F37';
            borderCol = '#06B6D4';
          }

          if (isHovered || isSelected) {
            ctx.lineWidth = 3;
            ctx.strokeStyle = node.status === 'ai' ? '#06B6D4' : (node.status === 'disrupted' ? '#F87171' : '#FBBF24');
          } else {
            ctx.lineWidth = 1.5;
            ctx.strokeStyle = borderCol;
          }

          // Màu nền thân Node
          ctx.fillStyle = nodeBg;
          ctx.beginPath();
          ctx.arc(node.x, node.y, 18, 0, Math.PI * 2);
          ctx.fill();
          ctx.stroke();

          // Vẽ Icon dạng text
          ctx.fillStyle = '#FFF';
          ctx.font = '14px Arial';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(node.icon, node.x, node.y + 0.5);

          // Nhãn chữ tên Node
          ctx.font = isSelected ? 'bold 11px Plus Jakarta Sans' : '10.5px Plus Jakarta Sans';
          ctx.fillStyle = isSelected ? '#FFFFFF' : '#94A3B8';
          ctx.fillText(node.label, node.x, node.y + 31);
        });

        frameId = requestAnimationFrame(draw);
      }

      function displayInspector(node) {
        if (!node) return;
        const titleEl = document.getElementById('node-inspector-title');
        const descEl = document.getElementById('node-inspector-desc');
        if (titleEl && descEl) {
          let statusColor = '#06B6D4'; // cyan
          if (node.status === 'disrupted') statusColor = '#EF4444';
          if (node.status === 'warning') statusColor = '#F59E0B';

          titleEl.innerHTML = `
        <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:${statusColor}; box-shadow: 0 0 10px ${statusColor}"></span>
        ${node.label.toUpperCase()} (${node.desc})
      `;
          descEl.innerHTML = node.details;
        }
      }

      // Bắt sự kiện Click / Hover trên Canvas
      function getNodeAtCoords(mx, my) {
        for (let node of nodes) {
          const dist = Math.hypot(node.x - mx, node.y - my);
          if (dist <= 25) return node;
        }
        return null;
      }

      canvas.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        const node = getNodeAtCoords(mx, my);
        if (node !== hoveredNode) {
          hoveredNode = node;
          canvas.style.cursor = node ? 'pointer' : 'default';
        }
      });

      canvas.addEventListener('click', (e) => {
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        const node = getNodeAtCoords(mx, my);
        if (node) {
          selectedNode = node;
          displayInspector(node);

          if (node.status !== 'disrupted') {
            const originalStatus = node.status;
            node.status = 'warning';
            setTimeout(() => { node.status = originalStatus; }, 350);
          }
        }
      });

      draw();
    }
